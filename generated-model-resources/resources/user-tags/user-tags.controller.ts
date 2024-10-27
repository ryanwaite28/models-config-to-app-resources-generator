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
import { UserTagService } from './user-tags.service';
import {
  UserTagExists,
  AuthUserOwnsUserTag
} from './user-tags.guard';
import { CreateUserTagDto } from "./user-tags.create.dto";
import { UpdateUserTagDto } from "./user-tags.update.dto";
import { SearchUserTagDto } from "./user-tags.search.dto";
import { JwtAuthorized } from '../../middlewares/jwt.middleware';
import { JwtUser } from '../../decorators/jwt.decorator';
import { MapType, JwtUserData } from '@app/shared';
import { FileUpload, FileUploadByName } from '../../decorators/file-upload.decorator';
import { UploadedFile } from 'express-fileupload';
import { Service } from 'typedi';



@Controller('/web/user-tags')
@Controller('/mobile/user-tags')
@Controller('/api/user-tags')
@Service()
export class UserTagController {
  
  constructor(private userTagService: UserTagService) {}


  @Get('/search')
  getUserTagBySearch(@QueryParams() query: SearchUserTagDto) {
    return this.userTagService.getUserTagBySearch(query);
  }

  @Get('/:id')
  getUserTagById(@Param('id') id: number) {
    return this.userTagService.getUserTagById(id);
  }

  @Post('')
  @UseBefore(JwtAuthorized)
  createUserTag(
    @JwtUser() user: JwtUserData,
    @BodyParam('payload', { validate: true }) dto: CreateUserTagDto,
    @FileUpload() files: MapType<UploadedFile>
  ) {
    return this.userTagService.createUserTag(user.id, dto, files);
  }

  @Put('/:id')
  @UseBefore(JwtAuthorized)
  updateUserTag(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateUserTagDto
  ) {
    return this.userTagService.updateUserTag(user.id, id, dto);
  }

  @Patch('/:id')
  @UseBefore(JwtAuthorized)
  patchUserTag(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateUserTagDto
  ) {
    return this.userTagService.patchUserTag(user.id, id, dto);
  }

  @Delete('/:id')
  @UseBefore(JwtAuthorized)
  deleteUserTag(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number
  ) {
    return this.userTagService.deleteUserTag(user.id, id);
  }
        
}