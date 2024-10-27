import 'reflect-metadata';
import {
  HttpStatusCodes,
  UserEntity,
  JwtUserData,
  S3ObjectEntity,
  UserTagEntity,
  MapType,
} from "@app/shared";
import { CreateUserTagDto } from "./user-tags.create.dto";
import { UpdateUserTagDto } from "./user-tags.update.dto";
import { SearchUserTagDto } from "./user-tags.search.dto";
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



export interface IUserTagService {
  getUserTagById(user_tag_id: number): Promise<UserTagEntity>;
  getUserTagBySearch(query: SearchUserTagDto): Promise<UserTagEntity[]>;
  createUserTag(user_id: number, dto: CreateUserTagDto, files?: MapType<UploadedFile>): Promise<UserTagEntity>;
  updateUserTag(user_id: number, user_tag_id: number, dto: UpdateUserTagDto): Promise<{ rows: number }>;
  patchUserTag(user_id: number, user_tag_id: number, dto: UpdateUserTagDto): Promise<{ rows: number }>;
  deleteUserTag(user_id: number, user_tag_id: number): Promise<{ rows: number }>;
}


@Service()
export class UserTagService implements IUserTagService {
  
  constructor(
    private repositoryService: RepositoryService,
    private awsS3Service: AwsS3Service,
    private socketService: SocketIoService,
  ) {}

  async getUserTagById(user_tag_id: number) {
    return this.repositoryService.userTagRepo.findOne({
      where: { id: user_tag_id }
    });
  }

  async getUserTagBySearch(query: SearchUserTagDto) {
    const parsedParams = parseQueryParams(query);
    // LOGGER.info('parsedParams', { parsedParams });
    const useLimit: number = (query['limit'] && INTEGER_REGEX.test(query['limit']))
      ? Math.min(100, parseInt(query['limit'], 10))
      : 10;
    return this.repositoryService.userTagRepo.findAll({
      where: parsedParams,
      limit: useLimit
    });
  }
  
  async createUserTag(user_id: number, dto: CreateUserTagDto, files?: MapType<UploadedFile>) {
    const s3Uploads: AwsS3UploadResults[] = [];
    let new_user_tag_id: number = null;
    
    try {
      // start a new database transaction
      await createTransaction(async (transaction) => {
        
        // create the UserTag record
        const new_user_tag = await this.repositoryService.userTagRepo.create({
          id: dto.id,
          metadata: dto.metadata,
          create_at: dto.create_at,
          updated_at: dto.updated_at,
          deleted_at: dto.deleted_at,
          user_id: dto.user_id,
          tag_id: dto.tag_id,
        }, { transaction });
        
        new_user_tag_id = new_user_tag.id;
        
        if (files) {
          /* Upload single file if needed
          const media_key = 'media';
          
          if (files[media_key]) {
            const file: UploadedFile = files[media_key];
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({
              model_type: ModelTypes.USER_TAG,
              model_id: new_user_tag.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }, { transaction });

            await this.repositoryService.userTagRepo.update({ media_id: s3Object.id }, { where: { id: new_user_tag.id }, transaction });
          }
          */

          /* Upload multiple files if needed
          const mediasKey = 'user_tag_media';
          const useFiles: UploadedFile[] = !files[mediasKey]
            ? []
            : Array.isArray(files[mediasKey])
              ? files[mediasKey]
              : [files[mediasKey]];

          for (const file of useFiles) {
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({
              model_type: ModelTypes.USER_TAG,
              model_id: new_user_tag.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }, { transaction });

            const new_user_tag_media = await this.repositoryService.___.create({
              user_tag_id: new_user_tag.id,
              media_id: s3Object.id,
              description: ''
            }, { transaction });
          }
          */
        }
        
      });
      
      const user_tag = await this.repositoryService.userTagRepo.findOne({
        where: { id: new_user_tag_id }
      });

      return user_tag;
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

      LOGGER.error('Error creating UserTag', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
        message: 'Could not create UserTag',
        context: error
      });
    }
    
  }
  
  async updateUserTag(user_id: number, user_tag_id: number, dto: UpdateUserTagDto) {
    const updates = await this.repositoryService.userTagRepo.update({
      id: dto.id,
      metadata: dto.metadata,
      create_at: dto.create_at,
      updated_at: dto.updated_at,
      deleted_at: dto.deleted_at,
      user_id: dto.user_id,
      tag_id: dto.tag_id,
    }, {
      where: {
        id: user_tag_id,
      }
    });
    return { rows: updates.rows };
  }
  
  async patchUserTag(user_id: number, user_tag_id: number, dto: UpdateUserTagDto) {
    const updateData = { ...dto };
    Object.keys(updateData).forEach((key) => {
      const isEmpty = (updateData[key] === null || updateData[key] === undefined);
      if (isEmpty) {
        delete updateData[key]
      }
    });
    const updates = await this.repositoryService.userTagRepo.update(updateData, {
      where: {
        id: user_tag_id,
      }
    });
    return { rows: updates.rows };
  }
  
  async deleteUserTag(user_id: number, user_tag_id: number) {
    const deletes = await this.repositoryService.userTagRepo.destroy({ 
      where: {
        id: user_tag_id,
      }
    });
    return { rows: deletes.results };
  }
        
}