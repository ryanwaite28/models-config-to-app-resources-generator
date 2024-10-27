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
  getUserBySearch(@QueryParams() query: SearchUserDto) {
    return this.userService.getUserBySearch(query);
  }

  @Get('/:id')
  getUserById(@Param('id') id: number) {
    return this.userService.getUserById(id);
  }

  @Post('')
  @UseBefore(JwtAuthorized)
  createUser(
    @JwtUser() user: JwtUserData,
    @BodyParam('payload', { validate: true }) dto: CreateUserDto,
    @FileUpload() files: MapType<UploadedFile>
  ) {
    return this.userService.createUser(user.id, dto, files);
  }

  @Put('/:id')
  @UseBefore(JwtAuthorized)
  updateUser(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateUserDto
  ) {
    return this.userService.updateUser(user.id, id, dto);
  }

  @Patch('/:id')
  @UseBefore(JwtAuthorized)
  patchUser(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({ validate: true }) dto: UpdateUserDto
  ) {
    return this.userService.patchUser(user.id, id, dto);
  }

  @Delete('/:id')
  @UseBefore(JwtAuthorized)
  deleteUser(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number
  ) {
    return this.userService.deleteUser(user.id, id);
  }
        
}