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
import { TagService } from './tags.service';
import {
  TagExists,
  AuthUserOwnsTag
} from './tags.guard';
import { CreateTagDto } from "./tags.create.dto";
import { UpdateTagDto } from "./tags.update.dto";
import { SearchTagDto } from "./tags.search.dto";
import { JwtAuthorized } from '../../middlewares/jwt.middleware';
import { JwtUser } from '../../decorators/jwt.decorator';
import { MapType, JwtUserData } from '@app/shared';
import { FileUpload, FileUploadByName } from '../../decorators/file-upload.decorator';
import { UploadedFile } from 'express-fileupload';
import { Service } from 'typedi';



@Controller('/web/tags')
@Controller('/mobile/tags')
@Controller('/api/tags')
@Service()
export class TagController {
  
  constructor(private tagService: TagService) {}


  @Get('/search')
  getTagBySearch(@QueryParams() query: SearchTagDto) {
    return this.tagService.getTagBySearch(query);
  }

  @Get('/:id')
  getTagById(@Param('id') id: number) {
    return this.tagService.getTagById(id);
  }

  @Post('')
  @UseBefore(JwtAuthorized)
  createTag(
    @JwtUser() user: JwtUserData,
    @BodyParam('payload', { validate: true }) dto: CreateTagDto,
    @FileUpload() files: MapType<UploadedFile>
  ) {
    return this.tagService.createTag(user.id, dto, files);
  }

  @Put('/:id')
  @UseBefore(JwtAuthorized)
  updateTag(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateTagDto
  ) {
    return this.tagService.updateTag(user.id, id, dto);
  }

  @Patch('/:id')
  @UseBefore(JwtAuthorized)
  patchTag(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateTagDto
  ) {
    return this.tagService.patchTag(user.id, id, dto);
  }

  @Delete('/:id')
  @UseBefore(JwtAuthorized)
  deleteTag(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number
  ) {
    return this.tagService.deleteTag(user.id, id);
  }
        
}