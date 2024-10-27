import { NextFunction, Request, Response } from 'express';
import {
  HttpStatusCodes,
  UserAuthProviderEntity,
} from '@app/shared';
import { Container } from "typedi";
import { USER_AUTH_PROVIDER_REPO_INJECT_TOKEN } from "./user-auth-providers.repository";



export async function UserAuthProviderExists(
  request: Request,
  response: Response,
  next: NextFunction
) {
  const id = parseInt(request.params.id, 10);
  const userAuthProviderRepo = Container.get(USER_AUTH_PROVIDER_REPO_INJECT_TOKEN);
  const userAuthProvider: UserAuthProviderEntity = await userAuthProviderRepo.findOne({ where: { id } });
  if (!userAuthProvider) {
    return response.status(HttpStatusCodes.NOT_FOUND).json({
      message: `UserAuthProvider does not exist by id: ${ id }`
    });
  }
  response.locals.userAuthProvider = userAuthProvider;
  return next();
}

export async function AuthUserOwnsUserAuthProvider(
  request: Request,
  response: Response,
  next: NextFunction
) {
  /* TODO: implement user ownership check 
  const userAuthProvider = response.locals.userAuthProvider as UserAuthProviderEntity;
  const isOwner = userAuthProvider.owner_id === request['auth'].id;
  if (!isOwner) {
    return response.status(HttpStatusCodes.FORBIDDEN).json({
      message: `User is not owner of UserAuthProvider by id: ${ userAuthProvider.id }`
    });
  }
  return next();
  */
}



