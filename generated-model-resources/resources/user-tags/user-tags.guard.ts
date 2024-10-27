import { NextFunction, Request, Response } from 'express';
import {
  HttpStatusCodes,
  UserTagEntity,
} from '@app/shared';
import { Container } from "typedi";
import { USER_TAG_REPO_INJECT_TOKEN } from "./user-tags.repository";



export async function UserTagExists(
  request: Request,
  response: Response,
  next: NextFunction
) {
  const id = parseInt(request.params.id, 10);
  const userTagRepo = Container.get(USER_TAG_REPO_INJECT_TOKEN);
  const userTag: UserTagEntity = await userTagRepo.findOne({ where: { id } });
  if (!userTag) {
    return response.status(HttpStatusCodes.NOT_FOUND).json({
      message: `UserTag does not exist by id: ${ id }`
    });
  }
  response.locals.userTag = userTag;
  return next();
}

export async function AuthUserOwnsUserTag(
  request: Request,
  response: Response,
  next: NextFunction
) {
  /* TODO: implement user ownership check 
  const userTag = response.locals.userTag as UserTagEntity;
  const isOwner = userTag.owner_id === request['auth'].id;
  if (!isOwner) {
    return response.status(HttpStatusCodes.FORBIDDEN).json({
      message: `User is not owner of UserTag by id: ${ userTag.id }`
    });
  }
  return next();
  */
}



