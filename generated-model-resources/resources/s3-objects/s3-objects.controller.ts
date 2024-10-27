import 'reflect-metadata';
import {
  Controller,
  Param,
  QueryParam,
  QueryParams,                 
  Body,
  BodyParam,
  Get,
  Post,
  Put,
  Delete,
  Patch,
  UseBefore,
} from 'routing-controllers';
import { S3ObjectService } from './s3-objects.service';
import {
  S3ObjectExists,
  AuthUserOwnsS3Object
} from './s3-objects.guard';
import { CreateS3ObjectDto } from "./dto/s3-objects.create.dto";
import { UpdateS3ObjectDto } from "./dto/s3-objects.update.dto";
import { SearchS3ObjectDto } from "./dto/s3-objects.search.dto";
import { JwtAuthorized } from '../../middlewares/jwt.middleware';
import { JwtUser } from '../../decorators/jwt.decorator';
import { MapType, JwtUserData } from '@app/shared';
import { FileUpload, FileUploadByName } from '../../decorators/file-upload.decorator';
import { UploadedFile } from 'express-fileupload';
import { Service } from 'typedi';



@Controller('/web/s3-objects')
@Controller('/mobile/s3-objects')
@Controller('/api/s3-objects')
@Service()
export class S3ObjectController {
  
  constructor(private s3ObjectService: S3ObjectService) {}


  @Get('/search')
  getS3ObjectBySearch(@QueryParams() query: SearchS3ObjectDto) {
    return this.s3ObjectService.getS3ObjectBySearch(query);
  }

  @Get('/:id')
  getS3ObjectById(@Param('id') id: number) {
    return this.s3ObjectService.getS3ObjectById(id);
  }

  @Post('')
  @UseBefore(JwtAuthorized)
  createS3Object(
    @JwtUser() user: JwtUserData,
    @BodyParam('payload', { validate: true }) dto: CreateS3ObjectDto,
    @FileUpload() files: MapType<UploadedFile>
  ) {
    return this.s3ObjectService.createS3Object(user.id, dto, files);
  }

  @Put('/:id')
  @UseBefore(JwtAuthorized)
  updateS3Object(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateS3ObjectDto
  ) {
    return this.s3ObjectService.updateS3Object(user.id, id, dto);
  }

  @Patch('/:id')
  @UseBefore(JwtAuthorized)
  patchS3Object(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateS3ObjectDto
  ) {
    return this.s3ObjectService.patchS3Object(user.id, id, dto);
  }

  @Delete('/:id')
  @UseBefore(JwtAuthorized)
  deleteS3Object(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number
  ) {
    return this.s3ObjectService.deleteS3Object(user.id, id);
  }
        
}