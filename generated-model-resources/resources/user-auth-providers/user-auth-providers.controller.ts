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
import { UserAuthProviderService } from './user-auth-providers.service';
import {
  UserAuthProviderExists,
  AuthUserOwnsUserAuthProvider
} from './user-auth-providers.guard';
import { CreateUserAuthProviderDto } from "./user-auth-providers.create.dto";
import { UpdateUserAuthProviderDto } from "./user-auth-providers.update.dto";
import { SearchUserAuthProviderDto } from "./user-auth-providers.search.dto";
import { JwtAuthorized } from '../../middlewares/jwt.middleware';
import { JwtUser } from '../../decorators/jwt.decorator';
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
  getUserAuthProviderBySearch(@QueryParams() query: SearchUserAuthProviderDto) {
    return this.userAuthProviderService.getUserAuthProviderBySearch(query);
  }

  @Get('/:id')
  getUserAuthProviderById(@Param('id') id: number) {
    return this.userAuthProviderService.getUserAuthProviderById(id);
  }

  @Post('')
  @UseBefore(JwtAuthorized)
  createUserAuthProvider(
    @JwtUser() user: JwtUserData,
    @BodyParam('payload', { validate: true }) dto: CreateUserAuthProviderDto,
    @FileUpload() files: MapType<UploadedFile>
  ) {
    return this.userAuthProviderService.createUserAuthProvider(user.id, dto, files);
  }

  @Put('/:id')
  @UseBefore(JwtAuthorized)
  updateUserAuthProvider(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateUserAuthProviderDto
  ) {
    return this.userAuthProviderService.updateUserAuthProvider(user.id, id, dto);
  }

  @Patch('/:id')
  @UseBefore(JwtAuthorized)
  patchUserAuthProvider(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateUserAuthProviderDto
  ) {
    return this.userAuthProviderService.patchUserAuthProvider(user.id, id, dto);
  }

  @Delete('/:id')
  @UseBefore(JwtAuthorized)
  deleteUserAuthProvider(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number
  ) {
    return this.userAuthProviderService.deleteUserAuthProvider(user.id, id);
  }
        
}