import { NextFunction, Request, Response } from 'express';
import {
  HttpStatusCodes,
  S3ObjectEntity,
} from '@app/shared';
import { Container } from "typedi";
import { S3_OBJECT_REPO_INJECT_TOKEN } from "./s3-objects.repository";



export async function S3ObjectExists(
  request: Request,
  response: Response,
  next: NextFunction
) {
  const id = parseInt(request.params.id, 10);
  const s3ObjectRepo = Container.get(S3_OBJECT_REPO_INJECT_TOKEN);
  const s3Object: S3ObjectEntity = await s3ObjectRepo.findOne({ where: { id } });
  if (!s3Object) {
    return response.status(HttpStatusCodes.NOT_FOUND).json({
      message: `S3Object does not exist by id: ${ id }`
    });
  }
  response.locals.s3Object = s3Object;
  return next();
}

export async function AuthUserOwnsS3Object(
  request: Request,
  response: Response,
  next: NextFunction
) {
  /* TODO: implement user ownership check 
  const s3Object = response.locals.s3Object as S3ObjectEntity;
  const isOwner = s3Object.owner_id === request['auth'].id;
  if (!isOwner) {
    return response.status(HttpStatusCodes.FORBIDDEN).json({
      message: `User is not owner of S3Object by id: ${ s3Object.id }`
    });
  }
  return next();
  */
}



