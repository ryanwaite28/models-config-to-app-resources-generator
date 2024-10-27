import 'reflect-metadata';
import {
  HttpStatusCodes,
  UserEntity,
  JwtUserData,
  S3ObjectEntity,
  UserAuthProviderEntity,
  MapType,
} from "@app/shared";
import { CreateUserAuthProviderDto } from "./user-auth-providers.create.dto";
import { UpdateUserAuthProviderDto } from "./user-auth-providers.update.dto";
import { SearchUserAuthProviderDto } from "./user-auth-providers.search.dto";
import { UploadedFile } from "express-fileupload";
import { AwsS3Service, AwsS3UploadResults } from "../../services/s3.aws.service";
import { ModelTypes } from "../../lib/constants/model-types.enum";
import {
  LOGGER,
  S3Objects,
  createTransaction,
  HttpRequestException,
  AppEnvironment
} from '@app/backend';
import { Includeable, col, literal } from "sequelize";
import { Service, Inject } from 'typedi';
import { getS3ObjectInclude } from "../../lib/utils/sequelize.utils";
import { SocketIoService } from '../../services/socket-io.service';
import { parseQueryParams } from '../../lib/utils/query-parser.utils';
import { INTEGER_REGEX } from '../../regex/common.regex';
import { RepositoryService } from '../../services/repository.service';



export interface IUserAuthProviderService {
  getUserAuthProviderById(user_auth_provider_id: number): Promise<UserAuthProviderEntity>;
  getUserAuthProviderBySearch(query: SearchUserAuthProviderDto): Promise<UserAuthProviderEntity[]>;
  createUserAuthProvider(user_id: number, dto: CreateUserAuthProviderDto, files?: MapType<UploadedFile>): Promise<UserAuthProviderEntity>;
  updateUserAuthProvider(user_id: number, user_auth_provider_id: number, dto: UpdateUserAuthProviderDto): Promise<{ rows: number }>;
  patchUserAuthProvider(user_id: number, user_auth_provider_id: number, dto: UpdateUserAuthProviderDto): Promise<{ rows: number }>;
  deleteUserAuthProvider(user_id: number, user_auth_provider_id: number): Promise<{ rows: number }>;
}


@Service()
export class UserAuthProviderService implements IUserAuthProviderService {
  
  constructor(
    private repositoryService: RepositoryService,
    private awsS3Service: AwsS3Service,
    private socketService: SocketIoService,
  ) {}

  async getUserAuthProviderById(user_auth_provider_id: number) {
    return this.repositoryService.userAuthProviderRepo.findOne({
      where: { id: user_auth_provider_id }
    });
  }

  async getUserAuthProviderBySearch(query: SearchUserAuthProviderDto) {
    const parsedParams = parseQueryParams(query);
    // LOGGER.info('parsedParams', { parsedParams });
    const useLimit: number = (query['limit'] && INTEGER_REGEX.test(query['limit']))
      ? Math.min(100, parseInt(query['limit'], 10))
      : 10;
    return this.repositoryService.userAuthProviderRepo.findAll({
      where: parsedParams,
      limit: useLimit
    });
  }
  
  async createUserAuthProvider(user_id: number, dto: CreateUserAuthProviderDto, files?: MapType<UploadedFile>) {
    const s3Uploads: AwsS3UploadResults[] = [];
    let new_user_auth_provider_id: number = null;
    
    try {
      // start a new database transaction
      await createTransaction(async (transaction) => {
        
        // create the UserAuthProvider record
        const new_user_auth_provider = await this.repositoryService.userAuthProviderRepo.create({
          id: dto.id,
          metadata: dto.metadata,
          create_at: dto.create_at,
          updated_at: dto.updated_at,
          deleted_at: dto.deleted_at,
          details: dto.details,
          user_id: dto.user_id,
          provider_name: dto.provider_name,
          provider_id: dto.provider_id,
        }, { transaction });
        
        new_user_auth_provider_id = new_user_auth_provider.id;
        
        if (files) {
          /* Upload single file if needed
          const media_key = 'media';
          
          if (files[media_key]) {
            const file: UploadedFile = files[media_key];
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({
              model_type: ModelTypes.USER_AUTH_PROVIDER,
              model_id: new_user_auth_provider.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }, { transaction });

            await this.repositoryService.userAuthProviderRepo.update({ media_id: s3Object.id }, { where: { id: new_user_auth_provider.id }, transaction });
          }
          */

          /* Upload multiple files if needed
          const mediasKey = 'user_auth_provider_media';
          const useFiles: UploadedFile[] = !files[mediasKey]
            ? []
            : Array.isArray(files[mediasKey])
              ? files[mediasKey]
              : [files[mediasKey]];

          for (const file of useFiles) {
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({
              model_type: ModelTypes.USER_AUTH_PROVIDER,
              model_id: new_user_auth_provider.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }, { transaction });

            const new_user_auth_provider_media = await this.repositoryService.___.create({
              user_auth_provider_id: new_user_auth_provider.id,
              media_id: s3Object.id,
              description: ''
            }, { transaction });
          }
          */
        }
        
      });
      
      const user_auth_provider = await this.repositoryService.userAuthProviderRepo.findOne({
        where: { id: new_user_auth_provider_id }
      });

      return user_auth_provider;
    }
    catch (error) {
      // transaction rollback; delete all uploaded s3 objects
      if (s3Uploads.length > 0) {
        for (const s3Upload of s3Uploads) {
          this.awsS3Service.deleteObject(s3Upload)
          .catch((error) => {
            LOGGER.error('s3 delete object error', { error, s3Upload });
          });
        }
      }

      LOGGER.error('Error creating UserAuthProvider', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
        message: 'Could not create UserAuthProvider',
        context: error
      });
    }
    
  }
  
  async updateUserAuthProvider(user_id: number, user_auth_provider_id: number, dto: UpdateUserAuthProviderDto) {
    const updates = await this.repositoryService.userAuthProviderRepo.update({
      id: dto.id,
      metadata: dto.metadata,
      create_at: dto.create_at,
      updated_at: dto.updated_at,
      deleted_at: dto.deleted_at,
      details: dto.details,
      user_id: dto.user_id,
      provider_name: dto.provider_name,
      provider_id: dto.provider_id,
    }, {
      where: {
        id: user_auth_provider_id,
      }
    });
    return { rows: updates.rows };
  }
  
  async patchUserAuthProvider(user_id: number, user_auth_provider_id: number, dto: UpdateUserAuthProviderDto) {
    const updateData = { ...dto };
    Object.keys(updateData).forEach((key) => {
      const isEmpty = (updateData[key] === null || updateData[key] === undefined);
      if (isEmpty) {
        delete updateData[key]
      }
    });
    const updates = await this.repositoryService.userAuthProviderRepo.update(updateData, {
      where: {
        id: user_auth_provider_id,
      }
    });
    return { rows: updates.rows };
  }
  
  async deleteUserAuthProvider(user_id: number, user_auth_provider_id: number) {
    const deletes = await this.repositoryService.userAuthProviderRepo.destroy({ 
      where: {
        id: user_auth_provider_id,
      }
    });
    return { rows: deletes.results };
  }
        
}