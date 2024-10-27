import { NextFunction, Request, Response } from 'express';
import {
  HttpStatusCodes,
  UserEntity,
} from '@app/shared';
import { Container } from "typedi";
import { USER_REPO_INJECT_TOKEN } from "./users.repository";



export async function UserExists(
  request: Request,
  response: Response,
  next: NextFunction
) {
  const id = parseInt(request.params.id, 10);
  const userRepo = Container.get(USER_REPO_INJECT_TOKEN);
  const user: UserEntity = await userRepo.findOne({ where: { id } });
  if (!user) {
    return response.status(HttpStatusCodes.NOT_FOUND).json({
      message: `User does not exist by id: ${ id }`
    });
  }
  response.locals.user = user;
  return next();
}

export async function AuthUserOwnsUser(
  request: Request,
  response: Response,
  next: NextFunction
) {
  /* TODO: implement user ownership check 
  const user = response.locals.user as UserEntity;
  const isOwner = user.owner_id === request['auth'].id;
  if (!isOwner) {
    return response.status(HttpStatusCodes.FORBIDDEN).json({
      message: `User is not owner of User by id: ${ user.id }`
    });
  }
  return next();
  */
}



