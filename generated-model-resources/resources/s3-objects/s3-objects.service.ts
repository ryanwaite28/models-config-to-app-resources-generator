import 'reflect-metadata';
import {
  HttpStatusCodes,
  UserEntity,
  JwtUserData,
  S3ObjectEntity,
  S3ObjectEntity,
  MapType,
} from "@app/shared";
import { CreateS3ObjectDto } from "./dto/s3-objects.create.dto";
import { UpdateS3ObjectDto } from "./dto/s3-objects.update.dto";
import { SearchS3ObjectDto } from "./dto/s3-objects.search.dto";
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



export interface IS3ObjectService {
  getS3ObjectById(s3_object_id: number): Promise<S3ObjectEntity>;
  getS3ObjectBySearch(query: SearchS3ObjectDto): Promise<S3ObjectEntity[]>;
  createS3Object(user_id: number, dto: CreateS3ObjectDto, files?: MapType<UploadedFile>): Promise<S3ObjectEntity>;
  updateS3Object(user_id: number, s3_object_id: number, dto: UpdateS3ObjectDto): Promise<{ rows: number }>;
  patchS3Object(user_id: number, s3_object_id: number, dto: UpdateS3ObjectDto): Promise<{ rows: number }>;
  deleteS3Object(user_id: number, s3_object_id: number): Promise<{ rows: number }>;
}


@Service()
export class S3ObjectService implements IS3ObjectService {
  
  constructor(
    private repositoryService: RepositoryService,
    private awsS3Service: AwsS3Service,
    private socketService: SocketIoService,
  ) {}

  async getS3ObjectById(s3_object_id: number) {
    return this.repositoryService.s3ObjectRepo.findOne({
      where: { id: s3_object_id }
    });
  }

  async getS3ObjectBySearch(query: SearchS3ObjectDto) {
    const parsedParams = parseQueryParams(query);
    // LOGGER.info('parsedParams', { parsedParams });
    const useLimit: number = (query['limit'] && INTEGER_REGEX.test(query['limit']))
      ? Math.min(100, parseInt(query['limit'], 10))
      : 10;
    return this.repositoryService.s3ObjectRepo.findAll({
      where: parsedParams,
      limit: useLimit
    });
  }
  
  async createS3Object(user_id: number, dto: CreateS3ObjectDto, files?: MapType<UploadedFile>) {
    const s3Uploads: AwsS3UploadResults[] = [];
    let new_s3_object_id: number = null;
    
    try {
      // start a new database transaction
      await createTransaction(async (transaction) => {
        
        // create the S3Object record
        const new_s3_object = await this.repositoryService.s3ObjectRepo.create({
          id: dto.id,
          metadata: dto.metadata,
          create_at: dto.create_at,
          updated_at: dto.updated_at,
          deleted_at: dto.deleted_at,
          model_type: dto.model_type,
          model_id: dto.model_id,
          mimetype: dto.mimetype,
          is_private: dto.is_private,
          region: dto.region,
          bucket: dto.bucket,
          key: dto.key,
        }, { transaction });
        
        new_s3_object_id = new_s3_object.id;
        
        if (files) {
          /* Upload single file if needed
          const media_key = 'media';
          
          if (files[media_key]) {
            const file: UploadedFile = files[media_key];
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({
              model_type: ModelTypes.S3_OBJECT,
              model_id: new_s3_object.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }, { transaction });

            await this.repositoryService.s3ObjectRepo.update({ media_id: s3Object.id }, { where: { id: new_s3_object.id }, transaction });
          }
          */

          /* Upload multiple files if needed
          const mediasKey = 's3_object_media';
          const useFiles: UploadedFile[] = !files[mediasKey]
            ? []
            : Array.isArray(files[mediasKey])
              ? files[mediasKey]
              : [files[mediasKey]];

          for (const file of useFiles) {
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({
              model_type: ModelTypes.S3_OBJECT,
              model_id: new_s3_object.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }, { transaction });

            const new_s3_object_media = await this.repositoryService.___.create({
              s3_object_id: new_s3_object.id,
              media_id: s3Object.id,
              description: ''
            }, { transaction });
          }
          */
        }
        
      });
      
      const s3_object = await this.repositoryService.s3ObjectRepo.findOne({
        where: { id: new_s3_object_id }
      });

      return s3_object;
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

      LOGGER.error('Error creating S3Object', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
        message: 'Could not create S3Object',
        context: error
      });
    }
    
  }
  
  async updateS3Object(user_id: number, s3_object_id: number, dto: UpdateS3ObjectDto) {
    const updates = await this.repositoryService.s3ObjectRepo.update({
      id: dto.id,
      metadata: dto.metadata,
      create_at: dto.create_at,
      updated_at: dto.updated_at,
      deleted_at: dto.deleted_at,
      model_type: dto.model_type,
      model_id: dto.model_id,
      mimetype: dto.mimetype,
      is_private: dto.is_private,
      region: dto.region,
      bucket: dto.bucket,
      key: dto.key,
    }, {
      where: {
        id: s3_object_id,
      }
    });
    return { rows: updates.rows };
  }
  
  async patchS3Object(user_id: number, s3_object_id: number, dto: UpdateS3ObjectDto) {
    const updateData = { ...dto };
    Object.keys(updateData).forEach((key) => {
      const isEmpty = (updateData[key] === null || updateData[key] === undefined);
      if (isEmpty) {
        delete updateData[key]
      }
    });
    const updates = await this.repositoryService.s3ObjectRepo.update(updateData, {
      where: {
        id: s3_object_id,
      }
    });
    return { rows: updates.rows };
  }
  
  async deleteS3Object(user_id: number, s3_object_id: number) {
    const deletes = await this.repositoryService.s3ObjectRepo.destroy({ 
      where: {
        id: s3_object_id,
      }
    });
    return { rows: deletes.results };
  }
        
}