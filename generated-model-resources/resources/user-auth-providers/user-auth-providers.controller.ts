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
import { UserAuthProviderService } from './user-auth-providers.service';
import {
  UserAuthProviderExists,
  AuthUserOwnsUserAuthProvider
} from './user-auth-providers.guard';
import { CreateUserAuthProviderDto } from "./dto/user-auth-providers.create.dto";
import { UpdateUserAuthProviderDto } from "./dto/user-auth-providers.update.dto";
import { SearchUserAuthProviderDto } from "./dto/user-auth-providers.search.dto";
import { JwtAuthorized } from '../../middlewares/jwt.middleware';
import { JwtUser } from '../../decorators/jwt.decorator';
import { UserAuthProvider } from '@app/shared';
import { MapType, JwtUserData } from '@app/shared';
import { FileUpload, FileUploadByName } from '../../decorators/file-upload.decorator';
import { UploadedFile } from 'express-fileupload';
import { Service } from 'typedi';



@Controller('/web/user-auth-providers')
@Controller('/mobile/user-auth-providers')
@Controller('/api/user-auth-providers')
@Service()
export class UserAuthProviderController {
  
  constructor(private userAuthProviderService: UserAuthProviderService) {}

  

  @Get('/search')
  @OpenAPI({
    description: 'Search UserAuthProviders',
    responses: {
      '200': {
        description: 'Search Successful',
        content: {
          'application/json': {
            schema: {
              type: 'array',
              items: {
                '$ref': '#/components/schemas/UserAuthProvider'
              }
            }
          }
        }
      }
    },
  })
  getUserAuthProviderBySearch(@QueryParams() query: SearchUserAuthProviderDto) {
    return this.userAuthProviderService.getUserAuthProviderBySearch(query);
  }

  @Get('/:id')
  @OpenAPI({
    description: 'Get UserAuthProvider by id',
    responses: {
      '200': {
        description: 'Get Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/UserAuthProvider'
            }
          }
        }
      }
    },
  })
  getUserAuthProviderById(@Param('id') id: number) {
    return this.userAuthProviderService.getUserAuthProviderById(id);
  }

  @Post('')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Create UserAuthProvider',
    responses: {
      '201': {
        description: 'Post Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/UserAuthProvider'
            }
          }
        }
      }
    },
  })
  createUserAuthProvider(
    @JwtUser() user: JwtUserData,
    @BodyParam('payload', { validate: true }) dto: CreateUserAuthProviderDto,
    @FileUpload() files: MapType<UploadedFile>
  ) {
    return this.userAuthProviderService.createUserAuthProvider(user.id, dto, files);
  }

  @Put('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Overwrite UserAuthProvider by id',
    responses: {
      '200': {
        description: 'Put Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/UserAuthProvider'
            }
          }
        }
      }
    },
  })
  updateUserAuthProvider(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateUserAuthProviderDto
  ) {
    return this.userAuthProviderService.updateUserAuthProvider(user.id, id, dto);
  }

  @Patch('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Update UserAuthProvider by id',
    responses: {
      '200': {
        description: 'Patch Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/UserAuthProvider'
            }
          }
        }
      }
    },
  })
  patchUserAuthProvider(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateUserAuthProviderDto
  ) {
    return this.userAuthProviderService.patchUserAuthProvider(user.id, id, dto);
  }

  @Delete('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Delete UserAuthProvider by id',
    responses: {
      '204': {
        description: 'Delete Successful'
      }
    },
  })
  deleteUserAuthProvider(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number
  ) {
    return this.userAuthProviderService.deleteUserAuthProvider(user.id, id);
  }
        
}