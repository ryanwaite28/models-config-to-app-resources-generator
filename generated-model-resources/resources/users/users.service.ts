import 'reflect-metadata';
import {
  HttpStatusCodes,
  UserEntity,
  JwtUserData,
  S3ObjectEntity,
  UserEntity,
  MapType,
} from "@app/shared";
import { CreateUserDto } from "./users.create.dto";
import { UpdateUserDto } from "./users.update.dto";
import { SearchUserDto } from "./users.search.dto";
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



export interface IUserService {
  getUserById(user_id: number): Promise<UserEntity>;
  getUserBySearch(query: SearchUserDto): Promise<UserEntity[]>;
  createUser(user_id: number, dto: CreateUserDto, files?: MapType<UploadedFile>): Promise<UserEntity>;
  updateUser(user_id: number, user_id: number, dto: UpdateUserDto): Promise<{ rows: number }>;
  patchUser(user_id: number, user_id: number, dto: UpdateUserDto): Promise<{ rows: number }>;
  deleteUser(user_id: number, user_id: number): Promise<{ rows: number }>;
}


@Service()
export class UserService implements IUserService {
  
  constructor(
    private repositoryService: RepositoryService,
    private awsS3Service: AwsS3Service,
    private socketService: SocketIoService,
  ) {}

  async getUserById(user_id: number) {
    return this.repositoryService.userRepo.findOne({
      where: { id: user_id }
    });
  }

  async getUserBySearch(query: SearchUserDto) {
    const parsedParams = parseQueryParams(query);
    // LOGGER.info('parsedParams', { parsedParams });
    const useLimit: number = (query['limit'] && INTEGER_REGEX.test(query['limit']))
      ? Math.min(100, parseInt(query['limit'], 10))
      : 10;
    return this.repositoryService.userRepo.findAll({
      where: parsedParams,
      limit: useLimit
    });
  }
  
  async createUser(user_id: number, dto: CreateUserDto, files?: MapType<UploadedFile>) {
    const s3Uploads: AwsS3UploadResults[] = [];
    let new_user_id: number = null;
    
    try {
      // start a new database transaction
      await createTransaction(async (transaction) => {
        
        // create the User record
        const new_user = await this.repositoryService.userRepo.create({
          id: dto.id,
          metadata: dto.metadata,
          create_at: dto.create_at,
          updated_at: dto.updated_at,
          deleted_at: dto.deleted_at,
          stripe_customer_account_id: dto.stripe_customer_account_id,
          stripe_account_id: dto.stripe_account_id,
          stripe_account_verified: dto.stripe_account_verified,
          stripe_identity_verified: dto.stripe_identity_verified,
          first_name: dto.first_name,
          last_name: dto.last_name,
          bio: dto.bio,
          icon_s3object_id: dto.icon_s3object_id,
          town: dto.town,
          city: dto.city,
          state: dto.state,
          zipcode: dto.zipcode,
          country: dto.country,
          tags: dto.tags,
          specialties: dto.specialties,
          person_verified: dto.person_verified,
          email_verified: dto.email_verified,
          phone_verified: dto.phone_verified,
        }, { transaction });
        
        new_user_id = new_user.id;
        
        if (files) {
          /* Upload single file if needed
          const media_key = 'media';
          
          if (files[media_key]) {
            const file: UploadedFile = files[media_key];
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({
              model_type: ModelTypes.USER,
              model_id: new_user.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }, { transaction });

            await this.repositoryService.userRepo.update({ media_id: s3Object.id }, { where: { id: new_user.id }, transaction });
          }
          */

          /* Upload multiple files if needed
          const mediasKey = 'user_media';
          const useFiles: UploadedFile[] = !files[mediasKey]
            ? []
            : Array.isArray(files[mediasKey])
              ? files[mediasKey]
              : [files[mediasKey]];

          for (const file of useFiles) {
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({
              model_type: ModelTypes.USER,
              model_id: new_user.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }, { transaction });

            const new_user_media = await this.repositoryService.___.create({
              user_id: new_user.id,
              media_id: s3Object.id,
              description: ''
            }, { transaction });
          }
          */
        }
        
      });
      
      const user = await this.repositoryService.userRepo.findOne({
        where: { id: new_user_id }
      });

      return user;
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

      LOGGER.error('Error creating User', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
        message: 'Could not create User',
        context: error
      });
    }
    
  }
  
  async updateUser(user_id: number, user_id: number, dto: UpdateUserDto) {
    const updates = await this.repositoryService.userRepo.update({
      id: dto.id,
      metadata: dto.metadata,
      create_at: dto.create_at,
      updated_at: dto.updated_at,
      deleted_at: dto.deleted_at,
      stripe_customer_account_id: dto.stripe_customer_account_id,
      stripe_account_id: dto.stripe_account_id,
      stripe_account_verified: dto.stripe_account_verified,
      stripe_identity_verified: dto.stripe_identity_verified,
      first_name: dto.first_name,
      last_name: dto.last_name,
      bio: dto.bio,
      icon_s3object_id: dto.icon_s3object_id,
      town: dto.town,
      city: dto.city,
      state: dto.state,
      zipcode: dto.zipcode,
      country: dto.country,
      tags: dto.tags,
      specialties: dto.specialties,
      person_verified: dto.person_verified,
      email_verified: dto.email_verified,
      phone_verified: dto.phone_verified,
    }, {
      where: {
        id: user_id,
      }
    });
    return { rows: updates.rows };
  }
  
  async patchUser(user_id: number, user_id: number, dto: UpdateUserDto) {
    const updateData = { ...dto };
    Object.keys(updateData).forEach((key) => {
      const isEmpty = (updateData[key] === null || updateData[key] === undefined);
      if (isEmpty) {
        delete updateData[key]
      }
    });
    const updates = await this.repositoryService.userRepo.update(updateData, {
      where: {
        id: user_id,
      }
    });
    return { rows: updates.rows };
  }
  
  async deleteUser(user_id: number, user_id: number) {
    const deletes = await this.repositoryService.userRepo.destroy({ 
      where: {
        id: user_id,
      }
    });
    return { rows: deletes.results };
  }
        
}