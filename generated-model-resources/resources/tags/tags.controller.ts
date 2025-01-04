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
import { TagService } from './tags.service';
import {
  TagExists,
  AuthUserOwnsTag
} from './tags.guard';
import { CreateTagDto } from "./dto/tags.create.dto";
import { UpdateTagDto } from "./dto/tags.update.dto";
import { SearchTagDto } from "./dto/tags.search.dto";
import { JwtAuthorized } from '../../middlewares/jwt.middleware';
import { JwtUser } from '../../decorators/jwt.decorator';
import { Tag } from '@app/shared';
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
  @OpenAPI({
    description: 'Search Tags',
    responses: {
      '200': {
        description: 'Search Successful',
        content: {
          'application/json': {
            schema: {
              type: 'array',
              items: {
                '$ref': '#/components/schemas/Tag'
              }
            }
          }
        }
      }
    },
  })
  getTagBySearch(@QueryParams() query: SearchTagDto) {
    return this.tagService.getTagBySearch(query);
  }

  @Get('/:id')
  @OpenAPI({
    description: 'Get Tag by id',
    responses: {
      '200': {
        description: 'Get Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/Tag'
            }
          }
        }
      }
    },
  })
  getTagById(@Param('id') id: number) {
    return this.tagService.getTagById(id);
  }

  @Post('')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Create Tag',
    responses: {
      '201': {
        description: 'Post Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/Tag'
            }
          }
        }
      }
    },
  })
  createTag(
    @JwtUser() user: JwtUserData,
    @BodyParam('payload', { validate: true }) dto: CreateTagDto,
    @FileUpload() files: MapType<UploadedFile>
  ) {
    return this.tagService.createTag(user.id, dto, files);
  }

  @Put('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Overwrite Tag by id',
    responses: {
      '200': {
        description: 'Put Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/Tag'
            }
          }
        }
      }
    },
  })
  updateTag(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateTagDto
  ) {
    return this.tagService.updateTag(user.id, id, dto);
  }

  @Patch('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Update Tag by id',
    responses: {
      '200': {
        description: 'Patch Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/Tag'
            }
          }
        }
      }
    },
  })
  patchTag(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateTagDto
  ) {
    return this.tagService.patchTag(user.id, id, dto);
  }

  @Delete('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Delete Tag by id',
    responses: {
      '204': {
        description: 'Delete Successful'
      }
    },
  })
  deleteTag(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number
  ) {
    return this.tagService.deleteTag(user.id, id);
  }
        
}