import {
  S3Client,
  PutObjectCommand,
  CreateBucketCommand,
  GetObjectCommand,
  DeleteObjectCommand,
  DeleteBucketCommand,
  HeadBucketCommand,
  PutObjectCommandOutput
} from "@aws-sdk/client-s3";
import { v4 as uuidv4 } from 'uuid';
import { UploadedFile } from "express-fileupload";
import { readFileSync } from "fs";
import { HttpStatusCodes, MapType, ServiceMethodResults } from "@app/shared";
import { AppEnvironment, HttpRequestException, LOGGER } from "@app/backend";
import { isImageFileOrBase64, upload_base64, upload_expressfile } from "../lib/utils/request-file.utils";
import { IUploadFile } from "../lib/interfaces/common.interface";
import { readFile } from 'fs/promises';
import { Service } from "typedi";



// Create an Amazon S3 service client object.
// const s3Client = AppEnvironment.IS_ENV.LOCAL
//   ? new S3({
//     endpoint: 'http://localhost:4566',  // required for localstack
//     accessKeyId: 'test',
//     secretAccessKey: 'test',
//     s3ForcePathStyle: true,  // required for localstack
//   })
//   : new S3({ region: AppEnvironment.AWS.S3.REGION });

const s3Client = AppEnvironment.IS_ENV.LOCAL
  ? new S3Client({
      region: AppEnvironment.AWS.S3.REGION,
      forcePathStyle: true,
      endpoint: AppEnvironment.AWS.S3.ENDPOINT,
      credentials: {
        accessKeyId: 'test',
        secretAccessKey: 'test',
      }
    })
  : new S3Client({ region: AppEnvironment.AWS.S3.REGION })

export type AwsS3UploadResults = {
  Region: string,
  Bucket: string,
  Key: string,
  ContentType: string,
  Link: string,
  S3Url: string,
  Id: string,
};

export interface IAwsS3Service {
  createBucket(Bucket: string): Promise<any>;
  createObject(params: {
    Bucket: string,
    Key: string,
    Body: any,
    ContentType: string
  }): Promise<any>;
  getObject(params: {
    Bucket: string,
    Key: string
  }): Promise<any>;
  deleteBucket(Bucket: string): Promise<any>;
  deleteObject(params: {
    Bucket: string,
    Key: string
  }): Promise<any>;
  bucketExists(Bucket: string): Promise<boolean>;
}

// https://www.npmjs.com/package/s3-upload-stream


@Service()
export class AwsS3Service implements IAwsS3Service {

  isS3ConventionId(id: string) {
    return id.includes(`${AppEnvironment.AWS.S3.BUCKET}|`);
  }

  async uploadBuffer(
    buffer: Buffer,
    params: {
      filename: string,
      mimetype: string,
    }
  ) {
    try {
      if (!buffer || buffer.byteLength === 0) {
        throw new HttpRequestException(HttpStatusCodes.BAD_REQUEST, {
          message: `buffer is missing/empty`
        });
      }
  
      const Key = `public/static/uploads/${params.mimetype.toLowerCase()}/${uuidv4()}.${Date.now()}.${params.filename}`;
      const Id = `${AppEnvironment.AWS.S3.BUCKET}|${Key}`; // unique id ref for database storage; makes it easy to figure out the bucket and key for later usages/purposes.
      const Link = `${AppEnvironment.AWS.S3.SERVE_ORIGIN}/${Key}`;
      const S3Url = `${AppEnvironment.AWS.S3.S3_URL}/${AppEnvironment.AWS.S3.BUCKET}/${Key}`;
  
      await this.createObject({
        Body: buffer,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: params.mimetype.toLowerCase()
      });
  
      LOGGER.info(`Web link to new upload: ${Link}`);
  
      const results: AwsS3UploadResults = {
        Region: AppEnvironment.AWS.S3.REGION,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: params.mimetype.toLowerCase(),
        Link,
        S3Url,
        Id
      };
  
      LOGGER.info(`AWS S3 upload results:`, { results });
  
      return results;
    }
    catch (error) {
      console.error('s3 error', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
        message: `Could not upload to AWS S3; something went wrong`,
        context: error
      });
    }
  }

  async uploadFile(file: UploadedFile) {
    try {
      if (!file || file.size === 0) {
        throw new HttpRequestException(HttpStatusCodes.BAD_REQUEST, {
          message: `file is missing/empty`
        });
      }
  
      const buffer: Buffer = await readFile(file.tempFilePath);
  
      if (!buffer || buffer.byteLength === 0) {
        throw new HttpRequestException(HttpStatusCodes.BAD_REQUEST, {
          message: `file buffer is missing/empty`
        });
      }
  
      const Key = `public/static/uploads/${file.mimetype.toLowerCase()}/${uuidv4()}.${Date.now()}.${file.name}`;
      const Id = `${AppEnvironment.AWS.S3.BUCKET}|${Key}`; // unique id ref for database storage; makes it easy to figure out the bucket and key for later usages/purposes.
      const Link = `${AppEnvironment.AWS.S3.SERVE_ORIGIN}/${Key}`;
      const S3Url = `${AppEnvironment.AWS.S3.S3_URL}/${AppEnvironment.AWS.S3.BUCKET}/${Key}`;
  
      await this.createObject({
        Body: buffer,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: file.mimetype.toLowerCase()
      });
  
      LOGGER.info(`Web link to new upload: ${Link}`);
  
      const results: AwsS3UploadResults = {
        Region: AppEnvironment.AWS.S3.REGION,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: file.mimetype.toLowerCase(),
        Link,
        S3Url,
        Id
      };
  
      LOGGER.info(`AWS S3 upload results:`, { results });
  
      return results;
    }
    catch (error) {
      console.error('s3 error', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
        message: `Could not upload to AWS S3; something went wrong`,
        context: error
      });
    }
  }

  async uploadFileWithValidation(
    file: string | UploadedFile,
    options?: {
      treatNotFoundAsError: boolean,
      validateAsImage?: boolean,
      mutateObj?: MapType,
      id_prop?: string,
      link_prop?: string;
    }
  ) {
    if (!file) {
      const serviceMethodResults: ServiceMethodResults = {
        status: HttpStatusCodes.BAD_REQUEST,
        error: options && options.hasOwnProperty('treatNotFoundAsError') ? options?.treatNotFoundAsError : true,
        info: {
          message: `No argument found/given`
        }
      };
      
      const errMsg = `AwsS3Service.uploadFile - ${options?.treatNotFoundAsError ? 'error' : 'info'}: no file input...`;
      options?.treatNotFoundAsError
        ? LOGGER.error(errMsg, { options, serviceMethodResults })
        : LOGGER.info(errMsg, { options, serviceMethodResults });
      return serviceMethodResults;
    }

    if (!!options?.validateAsImage && !isImageFileOrBase64(file)) {
      const serviceMethodResults: ServiceMethodResults = {
        status: HttpStatusCodes.BAD_REQUEST,
        error: true,
        info: {
          message: `Bad file input given.`
        }
      };
      return serviceMethodResults;
    }

    try {
      let filepath: string = '';
      let filetype: string = '';
      let filename: string = '';
      let filedata: IUploadFile = null;
      
      if (typeof file === 'string') {
        // base64 string provided; attempt parsing...
        filedata = await upload_base64(file);
        filepath = filedata.file_path;
        filetype = filedata.filetype;
        filename = filedata.filename;
      }
      else {
        filedata = await upload_expressfile(file);
        filetype = (<UploadedFile> file).mimetype;
        filepath = filedata.file_path;
        filename = filedata.filename;
      }

      if (!filetype || !filename || !filepath) {
        throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
          message: `file is missing data`,
          data: { filename, filepath, filetype, file }
        });
      }
  
      const Key = `public/static/uploads/${filetype.toLowerCase()}/${filename}`;
      const Id = `${AppEnvironment.AWS.S3.BUCKET}|${Key}`; // unique id ref for database storage; makes it easy to figure out the bucket and key for later usages/purposes.
      const Link = `${AppEnvironment.AWS.S3.SERVE_ORIGIN}/${Key}`;
      const S3Url = `${AppEnvironment.AWS.S3.S3_URL}/${AppEnvironment.AWS.S3.BUCKET}/${Key}`;

      const Body: Buffer = readFileSync(filepath);

      await this.createObject({
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        Body,
        ContentType: filetype.toLowerCase()
      });

      LOGGER.info(`Web link to new upload: ${Link}`);
  
      const results: AwsS3UploadResults = {
        Region: AppEnvironment.AWS.S3.REGION,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: filetype.toLowerCase(),
        Link,
        S3Url,
        Id
      };

      if (options && options.mutateObj && options.id_prop && options.link_prop) {
        options.mutateObj[options.id_prop] = Id;
        options.mutateObj[options.link_prop] = Link;
      }

      filedata?.remove();
  
      LOGGER.info(`AWS S3 upload results:`, { results });
      const serviceMethodResults: ServiceMethodResults<AwsS3UploadResults> = {
        status: HttpStatusCodes.OK,
        error: false,
        info: {
          data: results
        }
      };
      LOGGER.info(`AWS S3 upload results:`, { results });
      return serviceMethodResults;
    }
    catch (error) {
      const serviceMethodResults: ServiceMethodResults = {
        status: HttpStatusCodes.INTERNAL_SERVER_ERROR,
        error: true,
        info: {
          message: `Could not upload to AWS S3; something went wrong`
        }
      };
      LOGGER.error(serviceMethodResults.info.message || 'Error', { error });
      return serviceMethodResults;
    }
  }

  // create

  async createBucket(Bucket: string) {
    const data = await s3Client.send(new CreateBucketCommand({ Bucket }));
    console.log({ data, Bucket });
    LOGGER.info("Successfully created a bucket called:", { Bucket, data });
    return data; // For unit tests.
  }

  async createObject(params: {
    Bucket: string, // The name of the bucket. For example, 'sample_bucket_101'.
    Key: string, // The name of the object. For example, 'sample_upload.txt'.
    Body: any, // The content of the object. For example, 'Hello world!".
    ContentType: string
  }) {
    const results: PutObjectCommandOutput = await s3Client.send(new PutObjectCommand(params));
    delete params.Body;
    LOGGER.info(
      "Successfully created " +
      params.Key +
      " and uploaded it to " +
      params.Bucket +  "/" + params.Key +
      ", served as ",
      { results, params }
    );
    return results;
  }

  // get

  async getObject(params: {
    Bucket: string // The name of the bucket. For example, 'sample_bucket_101'.
    Key: string, // The name of the object. For example, 'sample_upload.txt'.
  }) {
    const results = await s3Client.send(new GetObjectCommand(params));
    LOGGER.info(
      "Successfully fetched " +
      params.Key +
      " and uploaded it to " +
      params.Bucket +
      "/" +
      params.Key,
      { results, params }
    );
    return results; // For unit tests.
  }

  // delete

  async deleteBucket(Bucket: string) {
    const data = await s3Client.send(new DeleteBucketCommand({ Bucket }));
    LOGGER.info(`Deleted Bucket ${Bucket}`, { data, Bucket });
    return data; // For unit tests.
  }

  async deleteObject(params: {
    Bucket: string, // The name of the bucket. For example, 'sample_bucket_101'.
    Key: string, // The name of the object. For example, 'sample_upload.txt'.
  }) {
    const results = await s3Client.send(new DeleteObjectCommand(params));
    LOGGER.info(
      "Successfully deleted " +
      params.Key +
      " from bucket " +
      params.Bucket,
      { results, params }
    );
    
    return results;
  }


  async bucketExists(Bucket: string): Promise<boolean> {
    try {
      const response = await s3Client.send(new HeadBucketCommand({ Bucket }));
      return true;
    }
    catch {
      return false;
    }
  }
}
