import 'reflect-metadata';
import {
  HttpStatusCodes,
  UserEntity,
  JwtUserData,
  S3ObjectEntity,
  TagEntity,
  MapType,
} from "@app/shared";
import { CreateTagDto } from "./tags.create.dto";
import { UpdateTagDto } from "./tags.update.dto";
import { SearchTagDto } from "./tags.search.dto";
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



export interface ITagService {
  getTagById(tag_id: number): Promise<TagEntity>;
  getTagBySearch(query: SearchTagDto): Promise<TagEntity[]>;
  createTag(user_id: number, dto: CreateTagDto, files?: MapType<UploadedFile>): Promise<TagEntity>;
  updateTag(user_id: number, tag_id: number, dto: UpdateTagDto): Promise<{ rows: number }>;
  patchTag(user_id: number, tag_id: number, dto: UpdateTagDto): Promise<{ rows: number }>;
  deleteTag(user_id: number, tag_id: number): Promise<{ rows: number }>;
}


@Service()
export class TagService implements ITagService {
  
  constructor(
    private repositoryService: RepositoryService,
    private awsS3Service: AwsS3Service,
    private socketService: SocketIoService,
  ) {}

  async getTagById(tag_id: number) {
    return this.repositoryService.tagRepo.findOne({
      where: { id: tag_id }
    });
  }

  async getTagBySearch(query: SearchTagDto) {
    const parsedParams = parseQueryParams(query);
    // LOGGER.info('parsedParams', { parsedParams });
    const useLimit: number = (query['limit'] && INTEGER_REGEX.test(query['limit']))
      ? Math.min(100, parseInt(query['limit'], 10))
      : 10;
    return this.repositoryService.tagRepo.findAll({
      where: parsedParams,
      limit: useLimit
    });
  }
  
  async createTag(user_id: number, dto: CreateTagDto, files?: MapType<UploadedFile>) {
    const s3Uploads: AwsS3UploadResults[] = [];
    let new_tag_id: number = null;
    
    try {
      // start a new database transaction
      await createTransaction(async (transaction) => {
        
        // create the Tag record
        const new_tag = await this.repositoryService.tagRepo.create({
          id: dto.id,
          metadata: dto.metadata,
          create_at: dto.create_at,
          updated_at: dto.updated_at,
          deleted_at: dto.deleted_at,
          name: dto.name,
          description: dto.description,
        }, { transaction });
        
        new_tag_id = new_tag.id;
        
        if (files) {
          /* Upload single file if needed
          const media_key = 'media';
          
          if (files[media_key]) {
            const file: UploadedFile = files[media_key];
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({
              model_type: ModelTypes.TAG,
              model_id: new_tag.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }, { transaction });

            await this.repositoryService.tagRepo.update({ media_id: s3Object.id }, { where: { id: new_tag.id }, transaction });
          }
          */

          /* Upload multiple files if needed
          const mediasKey = 'tag_media';
          const useFiles: UploadedFile[] = !files[mediasKey]
            ? []
            : Array.isArray(files[mediasKey])
              ? files[mediasKey]
              : [files[mediasKey]];

          for (const file of useFiles) {
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({
              model_type: ModelTypes.TAG,
              model_id: new_tag.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }, { transaction });

            const new_tag_media = await this.repositoryService.___.create({
              tag_id: new_tag.id,
              media_id: s3Object.id,
              description: ''
            }, { transaction });
          }
          */
        }
        
      });
      
      const tag = await this.repositoryService.tagRepo.findOne({
        where: { id: new_tag_id }
      });

      return tag;
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

      LOGGER.error('Error creating Tag', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
        message: 'Could not create Tag',
        context: error
      });
    }
    
  }
  
  async updateTag(user_id: number, tag_id: number, dto: UpdateTagDto) {
    const updates = await this.repositoryService.tagRepo.update({
      id: dto.id,
      metadata: dto.metadata,
      create_at: dto.create_at,
      updated_at: dto.updated_at,
      deleted_at: dto.deleted_at,
      name: dto.name,
      description: dto.description,
    }, {
      where: {
        id: tag_id,
      }
    });
    return { rows: updates.rows };
  }
  
  async patchTag(user_id: number, tag_id: number, dto: UpdateTagDto) {
    const updateData = { ...dto };
    Object.keys(updateData).forEach((key) => {
      const isEmpty = (updateData[key] === null || updateData[key] === undefined);
      if (isEmpty) {
        delete updateData[key]
      }
    });
    const updates = await this.repositoryService.tagRepo.update(updateData, {
      where: {
        id: tag_id,
      }
    });
    return { rows: updates.rows };
  }
  
  async deleteTag(user_id: number, tag_id: number) {
    const deletes = await this.repositoryService.tagRepo.destroy({ 
      where: {
        id: tag_id,
      }
    });
    return { rows: deletes.results };
  }
        
}