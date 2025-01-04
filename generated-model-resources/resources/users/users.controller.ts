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
import { UserService } from './users.service';
import {
  UserExists,
  AuthUserOwnsUser
} from './users.guard';
import { CreateUserDto } from "./dto/users.create.dto";
import { UpdateUserDto } from "./dto/users.update.dto";
import { SearchUserDto } from "./dto/users.search.dto";
import { JwtAuthorized } from '../../middlewares/jwt.middleware';
import { JwtUser } from '../../decorators/jwt.decorator';
import { User } from '@app/shared';
import { MapType, JwtUserData } from '@app/shared';
import { FileUpload, FileUploadByName } from '../../decorators/file-upload.decorator';
import { UploadedFile } from 'express-fileupload';
import { Service } from 'typedi';



@Controller('/web/users')
@Controller('/mobile/users')
@Controller('/api/users')
@Service()
export class UserController {
  
  constructor(private userService: UserService) {}

  

  @Get('/search')
  @OpenAPI({
    description: 'Search Users',
    responses: {
      '200': {
        description: 'Search Successful',
        content: {
          'application/json': {
            schema: {
              type: 'array',
              items: {
                '$ref': '#/components/schemas/User'
              }
            }
          }
        }
      }
    },
  })
  getUserBySearch(@QueryParams() query: SearchUserDto) {
    return this.userService.getUserBySearch(query);
  }

  @Get('/:id')
  @OpenAPI({
    description: 'Get User by id',
    responses: {
      '200': {
        description: 'Get Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/User'
            }
          }
        }
      }
    },
  })
  getUserById(@Param('id') id: number) {
    return this.userService.getUserById(id);
  }

  @Post('')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Create User',
    responses: {
      '201': {
        description: 'Post Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/User'
            }
          }
        }
      }
    },
  })
  createUser(
    @JwtUser() user: JwtUserData,
    @BodyParam('payload', { validate: true }) dto: CreateUserDto,
    @FileUpload() files: MapType<UploadedFile>
  ) {
    return this.userService.createUser(user.id, dto, files);
  }

  @Put('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Overwrite User by id',
    responses: {
      '200': {
        description: 'Put Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/User'
            }
          }
        }
      }
    },
  })
  updateUser(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateUserDto
  ) {
    return this.userService.updateUser(user.id, id, dto);
  }

  @Patch('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Update User by id',
    responses: {
      '200': {
        description: 'Patch Successful',
        content: {
          'application/json': {
            schema: {
              '$ref': '#/components/schemas/User'
            }
          }
        }
      }
    },
  })
  patchUser(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateUserDto
  ) {
    return this.userService.patchUser(user.id, id, dto);
  }

  @Delete('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({
    description: 'Delete User by id',
    responses: {
      '204': {
        description: 'Delete Successful'
      }
    },
  })
  deleteUser(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number
  ) {
    return this.userService.deleteUser(user.id, id);
  }
        
}