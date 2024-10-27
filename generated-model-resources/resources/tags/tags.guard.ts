import { NextFunction, Request, Response } from 'express';
import {
  HttpStatusCodes,
  TagEntity,
} from '@app/shared';
import { Container } from "typedi";
import { TAG_REPO_INJECT_TOKEN } from "./tags.repository";



export async function TagExists(
  request: Request,
  response: Response,
  next: NextFunction
) {
  const id = parseInt(request.params.id, 10);
  const tagRepo = Container.get(TAG_REPO_INJECT_TOKEN);
  const tag: TagEntity = await tagRepo.findOne({ where: { id } });
  if (!tag) {
    return response.status(HttpStatusCodes.NOT_FOUND).json({
      message: `Tag does not exist by id: ${ id }`
    });
  }
  response.locals.tag = tag;
  return next();
}

export async function AuthUserOwnsTag(
  request: Request,
  response: Response,
  next: NextFunction
) {
  /* TODO: implement user ownership check 
  const tag = response.locals.tag as TagEntity;
  const isOwner = tag.owner_id === request['auth'].id;
  if (!isOwner) {
    return response.status(HttpStatusCodes.FORBIDDEN).json({
      message: `User is not owner of Tag by id: ${ tag.id }`
    });
  }
  return next();
  */
}



