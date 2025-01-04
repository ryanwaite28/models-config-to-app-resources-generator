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
import { OpenAPI } from 'routing-controllers-openapi'
import { UserTagService } from './user-tags.service';
import {
  UserTagExists,
  AuthUserOwnsUserTag
} from './user-tags.guard';
import { CreateUserTagDto } from "./dto/user-tags.create.dto";
import { UpdateUserTagDto } from "./dto/user-tags.update.dto";
import { SearchUserTagDto } from "./dto/user-tags.search.dto";
import { JwtAuthorized } from '../../middlewares/jwt.middleware';
import { JwtUser } from '../../decorators/jwt.decorator';
import { UserTag } from '@app/shared';
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
  @OpenAPI({
    description: 'Search UserTags',
    responses: {
      '200': {
        description: 'Search Successful',
        content: {
          'application/json': {
            schema: {
              type: 'array',
              items: {
                '$ref': '#/components/schemas/UserTag'
              }
            }
          }
        }
      }
    },
  })
  getUserTagBySearch(@QueryParams() query: SearchUserTagDto) {
    return this.userTagService.getUserTagBySearch(query);
  }

  @Get('/:id')
  @OpenAPI({
    description: 'Get UserTag by id',
    responses: {
      '200': {
        description: 'Get Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/UserTag'
            }
          }
        }
      }
    },
  })
  getUserTagById(@Param('id') id: number) {
    return this.userTagService.getUserTagById(id);
  }

  @Post('')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Create UserTag',
    responses: {
      '201': {
        description: 'Post Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/UserTag'
            }
          }
        }
      }
    },
  })
  createUserTag(
    @JwtUser() user: JwtUserData,
    @BodyParam('payload', { validate: true }) dto: CreateUserTagDto,
    @FileUpload() files: MapType<UploadedFile>
  ) {
    return this.userTagService.createUserTag(user.id, dto, files);
  }

  @Put('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Overwrite UserTag by id',
    responses: {
      '200': {
        description: 'Put Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/UserTag'
            }
          }
        }
      }
    },
  })
  updateUserTag(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateUserTagDto
  ) {
    return this.userTagService.updateUserTag(user.id, id, dto);
  }

  @Patch('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Update UserTag by id',
    responses: {
      '200': {
        description: 'Patch Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/UserTag'
            }
          }
        }
      }
    },
  })
  patchUserTag(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateUserTagDto
  ) {
    return this.userTagService.patchUserTag(user.id, id, dto);
  }

  @Delete('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Delete UserTag by id',
    responses: {
      '204': {
        description: 'Delete Successful'
      }
    },
  })
  deleteUserTag(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number
  ) {
    return this.userTagService.deleteUserTag(user.id, id);
  }
        
}