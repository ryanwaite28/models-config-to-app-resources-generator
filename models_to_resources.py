import os, sys, re, json
from pathlib import Path
import lorem
from deepmerge import Merger



# https://pypi.org/project/deepmerge/
my_merger = Merger(
    # pass in a list of tuple, with the
    # strategies you are looking to apply
    # to each type.
    [
        (list, ["append"]),
        (dict, ["merge"]),
        (set, ["union"])
    ],
    # next, choose the fallback strategies,
    # applied to all other types:
    ["override"],
    # finally, choose the strategies in
    # the case where the types conflict:
    ["override"]
)



Path('generated-model-resources').mkdir(parents = True, exist_ok = True)



def camel_to_kebab(s):
    """Converts a camelCase string to kebab-case."""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s).lower()
    return s
  
def camel_to_snake(s):
    """Converts a camelCase string to snake-case."""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()
    return s
  
def pluralize(s: str) -> str:
  """Pluralizes a singular noun."""
  if s.endswith('s'):
    return s + 'es'
  elif s.endswith('ey'):
    return s + 's'
  elif s.endswith('y'):
    return s[:-1] + 'ies'
  else:
    return s + 's'
  
def format_updates_from_dto(f: str) -> str:
  '''
  f: str - a converted field name string from a sequelize model definition
  return example:
  
  name: dto.name,
  '''
  
  formatted = f"{f}: dto.{f},"
    
  # print ('formatted:')
  # print (formatted)

  return formatted


def format_dto_fields(f: str) -> str:
  decorated = (
    '  ' + ('@IsOptional()' if ('| null' in f) else '@IsDefined()') + '\n' + 
    '  ' + ('@IsString()' if (': string' in f) else '@IsBoolean()' if (': boolean' in f) else '@IsInt()' if (': number' in f) else '') + '\n' +
    '  ' + (f.replace(':', '?:') if ('| null' in f) else f) +
    '\n'
  )
    
  # print ('decorated:')
  # print (decorated)

  return decorated



def format_dto_fields_for_query(f: str) -> str:
  def format_number_field(f: str) -> str:
    return (
      '  ' + '@IsString()\n  @Matches(INTEGER_WITH_COMPARATOR_REGEX)\n' +
      '  ' + (f if ('| null' in f) else f.replace(';', ' | null;')).replace(':', '_op:').replace('number', 'string')
    )


  decorated = (
    '  @IsOptional()\n' + 
    ('  @IsString()\n  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)' if (': string' in f) else '  @IsBoolean()' if (': boolean' in f) else format_number_field(f) if (': number' in f) else '') + '\n' +
    # + (f.split(':')[0] + ': string | null;')
    '  ' + ('' if (': number' in f) else (f if ('| null' in f) else f.replace(';', ' | null;')))
    + '\n'
  )
    
  # print ('decorated:')
  # print (decorated)

  return decorated



  
  
  
user_owner_field_by_model = {}

field_names_by_model: dict[list[str]] = {}
relationships_definitions = []
field_definitions_by_model: dict[list[str]] = {}


def makeModelVarName(model_name: str) -> str:
  return model_name[0].lower() + model_name[1:]


def create_openapi_specs_from_model(model_name: str):
  kebob_name = camel_to_kebab(model_name)
  snake_name = camel_to_snake(model_name)
  
  model_name_plural = pluralize(model_name)
  model_var_name = makeModelVarName(model_name)
  
  singular = model_name.lower()
  plural = (singular[:-1] + 'ies') if (singular[-1] == 'y') else (singular + 's')
  
  kebob_name_plural = pluralize(kebob_name)
  snake_name_plural = pluralize(snake_name)
  
  singular_caps = singular.capitalize()
  plural_caps = plural.capitalize()

  model_properties = {}
  
  example_config = {}

  required_fields = []


  for field_def in field_definitions_by_model.get(model_name, []):

    field_name: str = field_def.split(':')[0].replace(' ', '')

    field_type = "string" if (': string' in field_def) else "boolean" if (': boolean' in field_def) else "integer" if (': number' in field_def) else None
    field_format = "date-time" if (('date' in field_def) or ('time' in field_def) or ('_at' in field_def)) else "boolean" if (': boolean' in field_def) else "int64" if (': number' in field_def) else "string"

    if not ('| null' in field_def):
      required_fields.append(field_name)

    model_field_property_config = {
      "type": field_type,
      "format": field_format,
      # "required": not ('| null' in field_def),
      # "nullable": ('| null' in field_def),
      "description": field_name.replace('_', ' ').capitalize()
    }

    model_properties[field_name] = model_field_property_config

    example_config[field_name] = "2024-01-01T00:00:00Z" if (field_type == "date-time") else "" if (field_type == 'string') else 1 if (field_type == 'integer') else True if (field_type == 'boolean') else None

  schema_definition = {
    f"{model_name}Entity": {
      "type": "object",
      "description": f"{model_name} entity",
      "properties": model_properties,
      "required": required_fields
    },
    f"Create{model_name}Dto": {
      "type": "object",
      "description": f"Create {model_name} DTO",
      "properties": model_properties
    },
    f"Update{model_name}Dto": {
      "type": "object",
      "description": f"Update {model_name} DTO",
      "properties": model_properties
    },
    f"Search{model_name}Dto": {
      "type": "object",
      "description": f"Search {model_name} DTO",
      "properties": model_properties
    }
  }

  specs = {
    "paths": {
      f"/{kebob_name_plural}": {
        "get": {
          "tags": [f"{model_name}"],
          "summary": f"Get all {model_name_plural}",
          "description": f"Get all {model_name_plural}",
          "operationId": f"get{model_name_plural}",
          "parameters": [],
          "responses": {
            "200": {
              "description": f"List of {model_name_plural}",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "array",
                    "items": {
                      "$ref": f"#/components/schemas/{model_name}Entity"
                    }
                  }
                }
              }
            }
          }
        },
        "post": {
          "tags": [f"{model_name}"],
          "summary": f"Create a new {model_name}",
          "description": f"Create a new {model_name}",
          "operationId": f"create{model_name}",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": f"#/components/schemas/Create{model_name}Dto"
                },
                "example": example_config
              }
            }
          },
          "responses": {
            "201": {
              "description": f"Created {model_name}",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": f"#/components/schemas/{model_name}Entity"
                  }
                }
              }
            }
          }
        }
      },
      f"/{kebob_name_plural}/search": {
        "get": {
          "tags": [f"{model_name}"],
          "summary": f"Get {model_name_plural} by search",
          "description": f"Get {plural} by search",
          "operationId": f"search{model_name_plural}",
          "parameters": [],
          "responses": {
            "200": {
              "description": f"List of {model_name_plural}",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "array",
                    "items": {
                      "$ref": f"#/components/schemas/Search{model_name}Dto"
                    }
                  }
                }
              }
            }
          }
        },
      },
      
      f"/{kebob_name_plural}/{{id}}": {
        "get": {
          "tags": [f"{model_name}"],
          "summary": f"Get {model_name} by ID",
          "description": f"Get {model_name} by ID",
          "operationId": f"get{model_name}ById",
          "parameters": [
            {
              "name": "id",
              "in": "path",
              "description": "ID of {model_name}",
              "required": True,
              "schema": {
                "type": "integer",
                "format": "int64"
              }
            }
          ],
          "responses": {
            "200": {
              "description": f"{model_name} found",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": f"#/components/schemas/{model_name}Entity"
                  }
                }
              }
            },
            "404": {
              "description": f"{singular_caps} not found"
            }
          }
        },
        "put": {
          "tags": [f"{model_name}"],
          "summary": f"Update {model_name} by ID",
          "description": f"Update {model_name} by ID",
          "operationId": f"update{model_name}",
          "parameters": [
            {
              "name": "id",
              "in": "path",
              "description": "ID of {model_name}",
              "required": True,
              "schema": {
                "type": "integer",
                "format": "int64"
              }
            }
          ],
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": f"#/components/schemas/Update{model_name}Dto"
                },
                "example": example_config
              }
            }
          },
          "responses": {
            "200": {
              "description": f"{model_name} updated",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": f"#/components/schemas/{model_name}Entity"
                  }
                }
              }
            },
            "404": {
              "description": f"{model_name} not found"
            }
          }
        },
        "patch": {
          "tags": [f"{model_name}"],
          "summary": f"Patch {model_name} by ID",
          "description": f"Patch {model_name} by ID",
          "operationId": f"Patch{model_name}",
          "parameters": [
            {
              "name": "id",
              "in": "path",
              "description": "ID of {model_name}",
              "required": True,
              "schema": {
                "type": "integer",
                "format": "int64"
              }
            }
          ],
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": f"#/components/schemas/Update{model_name}Dto"
                },
                "example": example_config
              }
            }
          },
          "responses": {
            "200": {
              "description": f"{model_name} updated",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": f"#/components/schemas/{model_name}Entity"
                  }
                }
              }
            },
            "404": {
              "description": f"{model_name} not found"
            }
          }
        },
        "delete": {
          "tags": [f"{model_name}"],
          "summary": f"Delete {model_name} by ID",
          "description": f"Delete {model_name} by ID",
          "operationId": f"delete{model_name}",
          "parameters": [
            {
              "name": "id",
              "in": "path",
              "description": "ID of {model_name}",
              "required": True,
              "schema": {
                "type": "integer",
                "format": "int64"
              }
            }
          ],
          "responses": {
            "204": {
              "description": f"{model_name} deleted"
            },
            "404": {
              "description": f"{model_name} not found"
            }
          }
        }
      }
    },
    "components": {
      "schemas": schema_definition
    }
  }

  


  return specs
  
  
def create_resource(
  model_name: str
):
    
  kebob_name = camel_to_kebab(model_name)
  snake_name = camel_to_snake(model_name)
  
  model_name_plural = pluralize(model_name)
  model_var_name = model_name[0].lower() + model_name[1:]
  
  singular = model_name.lower()
  plural = (singular[:-1] + 'ies') if (singular[-1] == 'y') else (singular + 's')
  
  kebob_name_plural = pluralize(kebob_name)
  snake_name_plural = pluralize(snake_name)
  
  singular_caps = singular.capitalize()
  plural_caps = plural.capitalize()
  
  # print('names: ', {
  #   "model_name": model_name,
  #   "kebob_name": kebob_name,
  #   "kebob_name_plural": kebob_name_plural,
  #   "snake_name": snake_name,
  #   "snake_name_plural": snake_name_plural,
  #   "model_name_plural": model_name_plural,
  #   "model_var_name": model_var_name,
  #   "singular": singular,
  #   "plural": plural,
  #   "singular_caps": singular_caps,
  #   "plural_caps": plural_caps,
  # })

  # base_path = f"src/apps/app-server/src/resources{plural}"
  base_path = 'generated-model-resources/resources'



  # if os.path.exists(base_path + f"/{kebob_name_plural}"):
  #   # print(f"Resource \"{model_name}\" already exists/created; exiting...")
  #   return


  Path(f"{base_path}/{kebob_name_plural}").mkdir(parents = True, exist_ok = True)
  Path(f"{base_path}/{kebob_name_plural}/dto").mkdir(parents = True, exist_ok = True)


  # files to create
  controller_file = Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.controller.ts")
  service_file = Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.service.ts")
  guard_file = Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.guard.ts")
  repository_file = Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.repository.ts")
  create_dto_file = Path(f"{base_path}/{kebob_name_plural}/dto/{kebob_name_plural}.create.dto.ts")
  update_dto_file = Path(f"{base_path}/{kebob_name_plural}/dto/{kebob_name_plural}.update.dto.ts")
  search_dto_file = Path(f"{base_path}/{kebob_name_plural}/dto/{kebob_name_plural}.search.dto.ts")
  
  
  controller_contents = (f'''\
import 'reflect-metadata';
import {{
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
}} from 'routing-controllers';
import {{ OpenAPI }} from 'routing-controllers-openapi'
import {{ {model_name}Service }} from './{kebob_name_plural}.service';
import {{
  {model_name}Exists,
  AuthUserOwns{model_name}
}} from './{kebob_name_plural}.guard';
import {{ Create{model_name}Dto }} from "./dto/{kebob_name_plural}.create.dto";
import {{ Update{model_name}Dto }} from "./dto/{kebob_name_plural}.update.dto";
import {{ Search{model_name}Dto }} from "./dto/{kebob_name_plural}.search.dto";
import {{ JwtAuthorized }} from '../../middlewares/jwt.middleware';
import {{ JwtUser }} from '../../decorators/jwt.decorator';
import {{ {model_name} }} from '@app/shared';
import {{ MapType, JwtUserData }} from '@app/shared';
import {{ FileUpload, FileUploadByName }} from '../../decorators/file-upload.decorator';
import {{ UploadedFile }} from 'express-fileupload';
import {{ Service }} from 'typedi';



@Controller('/web/{kebob_name_plural}')
@Controller('/mobile/{kebob_name_plural}')
@Controller('/api/{kebob_name_plural}')
@Service()
export class {model_name}Controller {{
  
  constructor(private {model_var_name}Service: {model_name}Service) {{}}

  

  @Get('/search')
  @OpenAPI({{
    description: 'Search {model_name_plural}',
    responses: {{
      '200': {{
        description: 'Search Successful',
        content: {{
          'application/json': {{
            schema: {{
              type: 'array',
              items: {{
                '$ref': '#/components/schemas/{model_name}'
              }}
            }}
          }}
        }}
      }}
    }},
  }})
  get{model_name}BySearch(@QueryParams() query: Search{model_name}Dto) {{
    return this.{model_var_name}Service.get{model_name}BySearch(query);
  }}

  @Get('/:id')
  @OpenAPI({{
    description: 'Get {model_name} by id',
    responses: {{
      '200': {{
        description: 'Get Successful',
        content: {{
          'application/json': {{
            schema: {{
              '$ref': '#/components/schemas/{model_name}'
            }}
          }}
        }}
      }}
    }},
  }})
  get{model_name}ById(@Param('id') id: number) {{
    return this.{model_var_name}Service.get{model_name}ById(id);
  }}

  @Post('')
  @UseBefore(JwtAuthorized)
  @OpenAPI({{
    description: 'Create {model_name}',
    responses: {{
      '201': {{
        description: 'Post Successful',
        content: {{
          'application/json': {{
            schema: {{
              '$ref': '#/components/schemas/{model_name}'
            }}
          }}
        }}
      }}
    }},
  }})
  create{model_name}(
    @JwtUser() user: JwtUserData,
    @BodyParam('payload', {{ validate: true }}) dto: Create{model_name}Dto,
    @FileUpload() files: MapType<UploadedFile>
  ) {{
    return this.{model_var_name}Service.create{model_name}(user.id, dto, files);
  }}

  @Put('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({{
    description: 'Overwrite {model_name} by id',
    responses: {{
      '200': {{
        description: 'Put Successful',
        content: {{
          'application/json': {{
            schema: {{
              '$ref': '#/components/schemas/{model_name}'
            }}
          }}
        }}
      }}
    }},
  }})
  update{model_name}(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({{ validate: true }}) dto: Update{model_name}Dto
  ) {{
    return this.{model_var_name}Service.update{model_name}(user.id, id, dto);
  }}

  @Patch('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({{
    description: 'Update {model_name} by id',
    responses: {{
      '200': {{
        description: 'Patch Successful',
        content: {{
          'application/json': {{
            schema: {{
              '$ref': '#/components/schemas/{model_name}'
            }}
          }}
        }}
      }}
    }},
  }})
  patch{model_name}(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({{ validate: true }}) dto: Update{model_name}Dto
  ) {{
    return this.{model_var_name}Service.patch{model_name}(user.id, id, dto);
  }}

  @Delete('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({{
    description: 'Delete {model_name} by id',
    responses: {{
      '204': {{
        description: 'Delete Successful'
      }}
    }},
  }})
  delete{model_name}(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number
  ) {{
    return this.{model_var_name}Service.delete{model_name}(user.id, id);
  }}
        
}}''')
  


  guard_contents = (f'''\
import {{ NextFunction, Request, Response }} from 'express';
import {{
  HttpStatusCodes,
  {model_name}Entity,
}} from '@app/shared';
import {{ Container }} from "typedi";
import {{ {snake_name.upper()}_REPO_INJECT_TOKEN }} from "./{kebob_name_plural}.repository";



export async function {model_name}Exists(
  request: Request,
  response: Response,
  next: NextFunction
) {{
  const id = parseInt(request.params.id, 10);
  const {model_var_name}Repo = Container.get({snake_name.upper()}_REPO_INJECT_TOKEN);
  const {model_var_name}: {model_name}Entity = await {model_var_name}Repo.findOne({{ where: {{ id }} }});
  if (!{model_var_name}) {{
    return response.status(HttpStatusCodes.NOT_FOUND).json({{
      message: `{model_name} does not exist by id: ${{ id }}`
    }});
  }}
  response.locals.{model_var_name} = {model_var_name};
  return next();
}}

export async function AuthUserOwns{model_name}(
  request: Request,
  response: Response,
  next: NextFunction
) {{
  /* TODO: implement user ownership check 
  const {model_var_name} = response.locals.{model_var_name} as {model_name}Entity;
  const isOwner = {model_var_name}.{user_owner_field_by_model.get(model_name, 'owner_id')} === request['auth'].id;
  if (!isOwner) {{
    return response.status(HttpStatusCodes.FORBIDDEN).json({{
      message: `User is not owner of {model_name} by id: ${{ {model_var_name}.id }}`
    }});
  }}
  return next();
  */
}}



''')
  

  service_contents = (f'''\
import 'reflect-metadata';
import {{
  HttpStatusCodes,
  UserEntity,
  JwtUserData,
  S3ObjectEntity,
  {model_name}Entity,
  MapType,
}} from "@app/shared";
import {{ Create{model_name}Dto }} from "./dto/{kebob_name_plural}.create.dto";
import {{ Update{model_name}Dto }} from "./dto/{kebob_name_plural}.update.dto";
import {{ Search{model_name}Dto }} from "./dto/{kebob_name_plural}.search.dto";
import {{ UploadedFile }} from "express-fileupload";
import {{ AwsS3Service, AwsS3UploadResults }} from "../../services/s3.aws.service";
import {{ ModelTypes }} from "../../lib/constants/model-types.enum";
import {{
  LOGGER,
  S3Objects,
  createTransaction,
  HttpRequestException,
  AppEnvironment
}} from '@app/backend';
import {{ Includeable, col, literal }} from "sequelize";
import {{ Service, Inject }} from 'typedi';
import {{ getS3ObjectInclude }} from "../../lib/utils/sequelize.utils";
import {{ SocketIoService }} from '../../services/socket-io.service';
import {{ parseQueryParams }} from '../../lib/utils/query-parser.utils';
import {{ INTEGER_REGEX }} from '../../regex/common.regex';
import {{ RepositoryService }} from '../../services/repository.service';



export interface I{model_name}Service {{
  get{model_name}ById({snake_name}_id: number): Promise<{model_name}Entity>;
  get{model_name}BySearch(query: Search{model_name}Dto): Promise<{model_name}Entity[]>;
  create{model_name}(user_id: number, dto: Create{model_name}Dto, files?: MapType<UploadedFile>): Promise<{model_name}Entity>;
  update{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto): Promise<{{ rows: number }}>;
  patch{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto): Promise<{{ rows: number }}>;
  delete{model_name}(user_id: number, {snake_name}_id: number): Promise<{{ rows: number }}>;
}}


@Service()
export class {model_name}Service implements I{model_name}Service {{
  
  constructor(
    private repositoryService: RepositoryService,
    private awsS3Service: AwsS3Service,
    private socketService: SocketIoService,
  ) {{}}

  async get{model_name}ById({snake_name}_id: number) {{
    return this.repositoryService.{model_var_name}Repo.findOne({{
      where: {{ id: {snake_name}_id }}
    }});
  }}

  async get{model_name}BySearch(query: Search{model_name}Dto) {{
    const parsedParams = parseQueryParams(query);
    // LOGGER.info('parsedParams', {{ parsedParams }});
    const useLimit: number = (query['limit'] && INTEGER_REGEX.test(query['limit']))
      ? Math.min(100, parseInt(query['limit'], 10))
      : 10;
    return this.repositoryService.{model_var_name}Repo.findAll({{
      where: parsedParams,
      limit: useLimit
    }});
  }}
  
  async create{model_name}(user_id: number, dto: Create{model_name}Dto, files?: MapType<UploadedFile>) {{
    const s3Uploads: AwsS3UploadResults[] = [];
    let new_{snake_name}_id: number = null;
    
    try {{
      // start a new database transaction
      await createTransaction(async (transaction) => {{
        
        // create the {model_name} record
        const new_{snake_name} = await this.repositoryService.{model_var_name}Repo.create({{
          {'\n          '.join([ (format_updates_from_dto(f)) for f in field_names_by_model.get(model_name, []) ])}
        }}, {{ transaction }});
        
        new_{snake_name}_id = new_{snake_name}.id;
        
        if (files) {{
          /* Upload single file if needed
          const media_key = 'media';
          
          if (files[media_key]) {{
            const file: UploadedFile = files[media_key];
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({{
              model_type: ModelTypes.{snake_name.upper()},
              model_id: new_{snake_name}.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }}, {{ transaction }});

            await this.repositoryService.{model_var_name}Repo.update({{ media_id: s3Object.id }}, {{ where: {{ id: new_{snake_name}.id }}, transaction }});
          }}
          */

          /* Upload multiple files if needed
          const mediasKey = '{snake_name}_media';
          const useFiles: UploadedFile[] = !files[mediasKey]
            ? []
            : Array.isArray(files[mediasKey])
              ? files[mediasKey]
              : [files[mediasKey]];

          for (const file of useFiles) {{
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({{
              model_type: ModelTypes.{snake_name.upper()},
              model_id: new_{snake_name}.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }}, {{ transaction }});

            const new_{snake_name}_media = await this.repositoryService.___.create({{
              {snake_name}_id: new_{snake_name}.id,
              media_id: s3Object.id,
              description: ''
            }}, {{ transaction }});
          }}
          */
        }}
        
      }});
      
      const {snake_name} = await this.repositoryService.{model_var_name}Repo.findOne({{
        where: {{ id: new_{snake_name}_id }}
      }});

      return {snake_name};
    }}
    catch (error) {{
      // transaction rollback; delete all uploaded s3 objects
      if (s3Uploads.length > 0) {{
        for (const s3Upload of s3Uploads) {{
          this.awsS3Service.deleteObject(s3Upload)
          .catch((error) => {{
            LOGGER.error('s3 delete object error', {{ error, s3Upload }});
          }});
        }}
      }}

      LOGGER.error('Error creating {model_name}', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {{
        message: 'Could not create {model_name}',
        context: error
      }});
    }}
    
  }}
  
  async update{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto) {{
    const updates = await this.repositoryService.{model_var_name}Repo.update({{
      {'\n      '.join([ (format_updates_from_dto(f)) for f in field_names_by_model.get(model_name, []) ])}
    }}, {{
      where: {{
        id: {snake_name}_id,{(f"\n        {user_owner_field_by_model.get(model_name, 'owner_id')}: user_id") if (model_name in user_owner_field_by_model) else ''}
      }}
    }});
    return {{ rows: updates.rows }};
  }}
  
  async patch{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto) {{
    const updateData = {{ ...dto }};
    Object.keys(updateData).forEach((key) => {{
      const isEmpty = (updateData[key] === null || updateData[key] === undefined);
      if (isEmpty) {{
        delete updateData[key]
      }}
    }});
    const updates = await this.repositoryService.{model_var_name}Repo.update(updateData, {{
      where: {{
        id: {snake_name}_id,{(f"\n        {user_owner_field_by_model.get(model_name, 'owner_id')}: user_id") if (model_name in user_owner_field_by_model) else ''}
      }}
    }});
    return {{ rows: updates.rows }};
  }}
  
  async delete{model_name}(user_id: number, {snake_name}_id: number) {{
    const deletes = await this.repositoryService.{model_var_name}Repo.destroy({{ 
      where: {{
        id: {snake_name}_id,{(f"\n        {user_owner_field_by_model.get(model_name, 'owner_id')}: user_id") if (model_name in user_owner_field_by_model) else ''}
      }}
    }});
    return {{ rows: deletes.results }};
  }}
        
}}''')
  


  repository_contents = (f'''\
import 'reflect-metadata';
import {{
  {model_name}Entity,
}} from "@app/shared";
import {{ sequelize_model_class_crud_to_entity_object, IModelCrud }} from "../../lib/utils/sequelize.utils";
import {{ {model_name_plural} }} from '@app/backend';
import {{ Container, Token }} from "typedi";




export const {snake_name.upper()}_REPO_INJECT_TOKEN = new Token<IModelCrud<{model_name}Entity>>('{snake_name.upper()}_REPO_INJECT_TOKEN');

const {model_name_plural}Repo: IModelCrud<{model_name}Entity> = sequelize_model_class_crud_to_entity_object<{model_name}Entity>({model_name_plural});

Container.set({snake_name.upper()}_REPO_INJECT_TOKEN, {model_name_plural}Repo);
        
''')



  create_dto_contents = (f'''\
import {{
  {model_name}Entity,
}} from "@app/shared";
import {{
  IsBoolean,
  IsEmail,
  IsIn,
  IsNotEmpty,
  IsDefined,
  IsOptional,
  IsString,
  IsNumber,
  IsInt,
  Matches,
  ValidateIf,
}} from 'class-validator';


export class Create{model_name}Dto implements Partial<{model_name}Entity> {{
  
{'\n'.join([ format_dto_fields(f) for f in field_definitions_by_model.get(model_name, []) ])}
}}

        
''')
    
    
    
  
    

  update_dto_contents = (f'''\
import {{
  {model_name}Entity,
}} from "@app/shared";
import {{
  IsBoolean,
  IsEmail,
  IsIn,
  IsNotEmpty,
  IsDefined,
  IsOptional,
  IsString,
  IsNumber,
  IsInt,
  Matches,
  ValidateIf,
}} from 'class-validator';


export class Update{model_name}Dto implements Partial<{model_name}Entity> {{
  
{'\n'.join([ format_dto_fields(f) for f in field_definitions_by_model.get(model_name, []) ])}
}}

        
''')
  

  search_dto_contents = (f'''\
import {{
  {model_name}Entity,
}} from "@app/shared";
import {{
  IsBoolean,
  IsEmail,
  IsIn,
  IsNotEmpty,
  IsDefined,
  IsOptional,
  IsString,
  IsNumber,
  IsInt,
  Matches,
  ValidateIf,
}} from 'class-validator';
import {{
  ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX,
  BOOLEAN_REGEX,
  INTEGER_WITH_COMPARATOR_REGEX,
}} from "../../../regex/common.regex";


export class Search{model_name}Dto implements Partial<{model_name}Entity> {{
  
{'\n'.join([ format_dto_fields_for_query(f) for f in field_definitions_by_model.get(model_name, []) ])}
}}

        
''')





  if not controller_file.is_file():
    with open(controller_file, 'w') as f:
      f.write(controller_contents)
    
  if not guard_file.is_file():
    with open(guard_file, 'w') as f:
      f.write(guard_contents)
    
  if not service_file.is_file():
    with open(service_file, 'w') as f:
      f.write(service_contents)
    
  if not repository_file.is_file():
    with open(repository_file, 'w') as f:
      f.write(repository_contents)
    
  if not create_dto_file.is_file():
    with open(create_dto_file, 'w') as f:
      f.write(create_dto_contents)
    
  if not update_dto_file.is_file():
    with open(update_dto_file, 'w') as f:
      f.write(update_dto_contents)
    
  if not search_dto_file.is_file():
    with open(search_dto_file, 'w') as f:
      f.write(search_dto_contents)


  # add copy to generated-model-resources for reference
  
  Path(f"generated-model-resources/resources/{kebob_name_plural}").mkdir(parents = True, exist_ok = True)
  Path(f"generated-model-resources/resources/{kebob_name_plural}/dto").mkdir(parents = True, exist_ok = True)
  Path(f"generated-model-resources/resources/{kebob_name_plural}/dto/validations").mkdir(parents = True, exist_ok = True)

  with open(Path(f"generated-model-resources/resources/{kebob_name_plural}/{kebob_name_plural}.controller.ts"), 'w') as f:
    f.write(controller_contents)
  
  with open(Path(f"generated-model-resources/resources/{kebob_name_plural}/{kebob_name_plural}.guard.ts"), 'w') as f:
    f.write(guard_contents)
  
  with open(Path(f"generated-model-resources/resources/{kebob_name_plural}/{kebob_name_plural}.service.ts"), 'w') as f:
    f.write(service_contents)
  
  with open(Path(f"generated-model-resources/resources/{kebob_name_plural}/{kebob_name_plural}.repository.ts"), 'w') as f:
    f.write(repository_contents)
  
  with open(Path(f"generated-model-resources/resources/{kebob_name_plural}/dto/{kebob_name_plural}.create.dto.ts"), 'w') as f:
    f.write(create_dto_contents)
  
  with open(Path(f"generated-model-resources/resources/{kebob_name_plural}/dto/{kebob_name_plural}.update.dto.ts"), 'w') as f:
    f.write(update_dto_contents)
  
  with open(Path(f"generated-model-resources/resources/{kebob_name_plural}/dto/{kebob_name_plural}.search.dto.ts"), 'w') as f:
    f.write(search_dto_contents)
  


def getFieldDef(field, field_config):
  return f'{field}: {'string' if (field_config['dataType'] in ['string', 'text', 'datetime', 'uuid', 'json', 'jsonb']) else 'number' if (field_config['dataType'] in ['integer', 'float', 'double', 'number']) else 'boolean'}{' | null' if not (field_config['required']) else ''};'


def convert_models_to_resources():
  
  global user_owner_field_by_model
  global field_definitions_by_model
  global field_names_by_model



  openapi_specs = {
    "openapi": "3.0.0",
    "info": {
      "title": "Denaly | API",
      "description": "Swagger UI for Denaly API",
      "termsOfService": "https://example.com/terms/",
      "contact": {
        "name": "API Support",
        "url": "https://www.example.com/support",
        "email": "support@example.com"
      },
      "license": {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
      },
      "version": "1.0.1"
    },
    "servers": [
      {
        "url": "http://localhost:4000/web",
        "description": "Local server"
      },
      {
        "url": "https://development.gigantic-server.com",
        "description": "Development server"
      },
      {
        "url": "https://staging.gigantic-server.com",
        "description": "Staging server"
      },
      {
        "url": "https://api.gigantic-server.com",
        "description": "Production server"
      }
    ],
  }
  

  
  interface_file_contents = [
    "export interface _BaseEntity {}",
    "\n\n\n"
  ]

  models_file_cotents = []
  model_relationships_file_cotents = []
  
  contents: dict = {}

  with open("model-to-resource.config.json", 'r') as f:
    contents = json.loads(f.read())
    
  relationships_definitions = contents.get("relationships", {})

  model_names = contents.get("models", {}).keys()

  if not model_names or len(model_names) == 0:
    print("No models found in config.")
    return
  
  for model_name in model_names:

    model_config = contents.get("models", {}).get(model_name, {})

    fields = model_config.get('fields', {})
    
    field_names = fields.keys()

    field_names_by_model[model_name] = field_names

    field_definitions_by_model[model_name] = [getFieldDef(field, fields[field]) for field in field_names]
    


    interface_contents = f'''\
export interface {model_name}Entity extends _BaseEntity {{
  {'\n  '.join(field_definitions_by_model[model_name])}
  <relationships>
}}
  '''
    
    model_object_contents = f'''\
export const {model_name} = sequelize.define({f'"{model_config['tableName']}"'}, {{
  {'\n  '.join([ f"{field}: {{ type: DataTypes.{fields[field]['dataType'].upper()}, allowNull: {'false' if (fields[field]['required']) else 'true'}{', primaryKey: true, autoIncrement: true' if fields[field].get('primaryKey', False) else ''} }}," for field in field_names ])}
}});
  '''
# }}, {{ indexes: [{{ unique: f{'true' if model_config.get('indexes', {}).get('unique', False) else 'false'}, fields: [{ ', '.join([]) }] }}] }});

    relationships = relationships_definitions.get(model_name, None)
    if not relationships:
      interface_contents = interface_contents.replace("\n  <relationships>", "")
    else:
      relationship_contents = []

      relationshipsHasOne = relationships.get("hasOne", {})
      relationshipsHasMany = relationships.get("hasMany", {})
      relationshipsBelongsTo = relationships.get("belongsToOne", {})
      relationshipsBelongsToMany = relationships.get("belongsToMany", {})

      for model in relationshipsHasOne.keys():
        relationship_contents.append(f'{relationshipsHasOne[model]['alias']}?: {model}Entity;')
        model_relationships_file_cotents.append(f'{model_name}.hasOne({model}, {{ as: "{relationshipsHasOne[model]['alias']}", foreignKey: "{relationshipsHasOne[model]['foreignKey']}", sourceKey: "{relationshipsHasOne[model]['sourceKey']}" }});')
      
      for model in relationshipsHasMany.keys():
        relationship_contents.append(f'{relationshipsHasMany[model]['alias']}?: {model}Entity[];')
        model_relationships_file_cotents.append(f'{model_name}.hasMany({model}, {{ as: "{relationshipsHasMany[model]['alias']}", foreignKey: "{relationshipsHasMany[model]['foreignKey']}", sourceKey: "{relationshipsHasMany[model]['sourceKey']}" }});')
      
      for model in relationshipsBelongsTo.keys():
        relationship_contents.append(f'{relationshipsBelongsTo[model]['alias']}?: {model}Entity;')
        model_relationships_file_cotents.append(f'{model_name}.belongsTo({model}, {{ as: "{relationshipsBelongsTo[model]['alias']}", foreignKey: "{relationshipsBelongsTo[model]['foreignKey']}", targetKey: "{relationshipsBelongsTo[model]['targetKey']}" }});')
      
      for model in relationshipsBelongsToMany.keys():
        relationship_contents.append(f'{relationshipsBelongsToMany[model]['alias']}?: {model}Entity[];')
        model_relationships_file_cotents.append(f'{model_name}.belongsToMany({model}, {{ as: "{relationshipsBelongsToMany[model]['alias']}", foreignKey: "{relationshipsBelongsToMany[model]['foreignKey']}", targetKey: "{relationshipsBelongsToMany[model]['targetKey']}" }});')

      interface_contents = interface_contents.replace("<relationships>", "\n  " + "\n  ".join(relationship_contents))
      
    interface_file_contents.append(interface_contents)

    models_file_cotents.append(model_object_contents)

    create_resource(model_name = model_name)

    model_openapi_specs = create_openapi_specs_from_model(model_name = model_name)

    my_merger.merge(openapi_specs, model_openapi_specs)

    

    has_user_owner_field: bool = False

    for field in field_names:
      field_config = fields[field]
      if field_config.get("references", {}).get("model", "") == "User":
        user_owner_field_by_model[model_name] = field
        has_user_owner_field = True
        break
    
    if has_user_owner_field:
      user_owner_field_by_model[model_name] = field

  joined_interface_contents = "\n\n".join(interface_file_contents)

  models_file_cotents.extend(model_relationships_file_cotents)
  joined_model_object_contents = "\n\n".join(models_file_cotents)

  with open(f"generated-model-resources/model-interfaces-converted.ts", 'w') as f:
    f.write(joined_interface_contents)

  with open(f"generated-model-resources/models.sequelize.ts", 'w') as f:
    f.write(joined_model_object_contents)


  model_types_contents = [
    'export enum ModelTypes {\n',
  ]
  for model_name in model_names:
    snake_name = camel_to_snake(model_name)
    model_types_contents.append(f'  {snake_name.upper()} = "{snake_name.upper()}",\n')
  model_types_contents.append('}\n')
    
  with open(f"generated-model-resources/model-types-converted.enum.ts", 'w') as f:
    f.write(''.join(model_types_contents))

  
  print(field_definitions_by_model)
    


  repository_service_contents = (f'''\
import 'reflect-metadata';
import {{ Service, Inject }} from "typedi";
import {{ IModelCrud }} from "../lib/utils/sequelize.utils";
import {{
  {'\n  '.join([ f"{model_name}Entity," for model_name in model_names ])}
}} from '@app/shared';
{'\n'.join([ f"import {{ {camel_to_snake(model_name).upper()}_REPO_INJECT_TOKEN }} from '../resources/{pluralize(camel_to_kebab(model_name))}/{pluralize(camel_to_kebab(model_name))}.repository';" for model_name in model_names ])}

                                 
@Service()
export class RepositoryService {{
                                 
  constructor(
    {'''\n    '''.join([ f"@Inject({camel_to_snake(model_name).upper()}_REPO_INJECT_TOKEN) public readonly {(model_name[0].lower() + model_name[1:])}Repo: IModelCrud<{model_name}Entity>," for model_name in model_names ])}
  ) {{}}
                                 
}}
        
''')
  
  regex_contents = ('''\
export const AUTH_BEARER_HEADER_REGEX: RegExp = /Bearer\s[^]/;
export const GENERIC_TEXT_REGEX: RegExp = /^[a-zA-Z0-9\s\'\-\_\.\@\$\#]{1,250}/;
export const PERSON_NAME_REGEX: RegExp = /^[a-zA-Z\s\'\-\_\.]{2,50}$/;
export const URL_REGEX = /[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi;
export const BASE64_REGEX = /^data:([A-Za-z-+\/]+);base64,(.+)$/;
export const MENTIONS_REGEX = /@[a-zA-Z0-9\-\_\.]{2,50}/gi;

export const YOUTUBE_URL_STANDARD = /http(s?):\/\/(www\.)?youtube\.com\/watch\?(.*)/gi;
export const YOUTUBE_URL_SHORT = /http(s?):\/\/(www\.)?youtu\.be\/(.*)/gi;
export const YOUTUBE_URL_EMBED = /http(s?):\/\/(www\.)?youtube\.com\/embed\/(.*)/gi;
export const YOUTUBE_URL_ID = /(v=[a-zA-Z0-9\-\_]{7,}|\/[a-zA-Z0-9\-\_]{7,})/gi;

export const LEADING_SPACES = /[\s]{2,}/;
export const LEADING_SPACES_GLOBAL = /[\s]{2,}/gi;

export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
// export const PHONE_NUMBER_REGEX = /^\+?[1-9]\d{1,14}$/;
export const PHONE_NUMBER_REGEX = /^\+1\d{10}$/;
export const ZIP_CODE_REGEX = /^\d{5}$/;
export const IP_ADDRESS_REGEX = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
export const MAC_ADDRESS_REGEX = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/;
export const UUID_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$/;
export const ISO_DATE_REGEX = /^\d{4}-\d{2}-\d{2}$/;
export const ISO_TIME_REGEX = /^\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})?$/;
export const ISO_DATE_TIME_REGEX = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})?$/;
export const ISO_OFFSET_REGEX = /^\d{2}:\d{2}$/;
export const COMMA_SEPARATED_LIST_REGEX = /^(\w+(?:\s*,\s*\w+)*)$/;
export const COMMA_SEPARATED_LIST_REGEX2 = /(([^,]+),?)/;
export const SEMICOLON_SEPARATED_LIST_REGEX = /^(\w+(?:\s*;\s*\w+)*)$/;

export const PERCENTAGE_REGEX = /^(\d{1,3}%)$/;
export const INTEGER_REGEX = /^(\d+)$/;
export const DECIMAL_REGEX = /^(\d+(?:\.\d*)?)$/;
export const TIME_REGEX = /^(\d{2}:\d{2}:\d{2})$/;
export const DATE_REGEX = /^(\d{4}-\d{2}-\d{2})$/;
export const DATETIME_REGEX = /^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})$/;
export const UUID_V4_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V5_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-5[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V6_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[6789AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V7_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-7[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V8_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-8[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V9_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-9[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V10_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-A[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V11_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-B[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V12_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-C[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;

export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_REGEX = /^[a-zA-Z0-9\s\-\_]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_REGEX = /^[a-zA-Z0-9\s\-\_\.\@]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_REGEX = /^[a-zA-Z0-9\s\-\_\.\,]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_REGEX = /^[a-zA-Z0-9\s\-\_\.\,\:]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX = /^[a-zA-Z0-9\s\-\_\.\,\:\/]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_BRACKET_REGEX = /^[a-zA-Z0-9\s\-\_\.\,\:\/\[\]]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_BRACKET_PARENTHESIS_REGEX = /^[a-zA-Z0-9\s\-\_\.\,\:\/\[\]\(\)]{1,250}$/;

export const BOOLEAN_REGEX = /^(true|false)$/;

export const INTEGER_WITH_COMPARATOR_REGEX = /(^(eq|ne|gt|lt|gte|lte)<(\d+)>$|^(between|notBetween)<([\d]+,[\d]+)>$|^(in|notIn)<([\d]+(,[\d]+)*)>$)/;
// day of the week regex
export const DAY_OF_WEEK_REGEX = /^(mon|tue|wed|thu|fri|sat|sun)$/;
// full day of the week regex
// export const FULL_DAY_OF_WEEK_REGEX = /^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$/;
export const DAYS_OF_THE_WEEK_REGEX = /^(?:sunday,?)?(?:monday,?)?(?:tuesday,?)?(?:wednesday,?)?(?:thursday,?)?(?:friday,?)?(?:saturday,?)?$/;
''')
  
  aws_s3_service = ('''\
import {
  S3Client,
  PutObjectCommand,
  CreateBucketCommand,
  GetObjectCommand,
  DeleteObjectCommand,
  DeleteBucketCommand,
  HeadBucketCommand,
  PutObjectCommandOutput
} from "@aws-sdk/client-s3";
import { v4 as uuidv4 } from 'uuid';
import { UploadedFile } from "express-fileupload";
import { readFileSync } from "fs";
import { HttpStatusCodes, MapType, ServiceMethodResults } from "@app/shared";
import { AppEnvironment, HttpRequestException, LOGGER } from "@app/backend";
import { isImageFileOrBase64, upload_base64, upload_expressfile } from "../lib/utils/request-file.utils";
import { IUploadFile } from "../lib/interfaces/common.interface";
import { readFile } from 'fs/promises';
import { Service } from "typedi";



// Create an Amazon S3 service client object.
// const s3Client = AppEnvironment.IS_ENV.LOCAL
//   ? new S3({
//     endpoint: 'http://localhost:4566',  // required for localstack
//     accessKeyId: 'test',
//     secretAccessKey: 'test',
//     s3ForcePathStyle: true,  // required for localstack
//   })
//   : new S3({ region: AppEnvironment.AWS.S3.REGION });

const s3Client = AppEnvironment.IS_ENV.LOCAL
  ? new S3Client({
      region: AppEnvironment.AWS.S3.REGION,
      forcePathStyle: true,
      endpoint: AppEnvironment.AWS.S3.ENDPOINT,
      credentials: {
        accessKeyId: 'test',
        secretAccessKey: 'test',
      }
    })
  : new S3Client({ region: AppEnvironment.AWS.S3.REGION })

export type AwsS3UploadResults = {
  Region: string,
  Bucket: string,
  Key: string,
  ContentType: string,
  Link: string,
  S3Url: string,
  Id: string,
};

export interface IAwsS3Service {
  createBucket(Bucket: string): Promise<any>;
  createObject(params: {
    Bucket: string,
    Key: string,
    Body: any,
    ContentType: string
  }): Promise<any>;
  getObject(params: {
    Bucket: string,
    Key: string
  }): Promise<any>;
  deleteBucket(Bucket: string): Promise<any>;
  deleteObject(params: {
    Bucket: string,
    Key: string
  }): Promise<any>;
  bucketExists(Bucket: string): Promise<boolean>;
}

// https://www.npmjs.com/package/s3-upload-stream


@Service()
export class AwsS3Service implements IAwsS3Service {

  isS3ConventionId(id: string) {
    return id.includes(`${AppEnvironment.AWS.S3.BUCKET}|`);
  }

  async uploadBuffer(
    buffer: Buffer,
    params: {
      filename: string,
      mimetype: string,
    }
  ) {
    try {
      if (!buffer || buffer.byteLength === 0) {
        throw new HttpRequestException(HttpStatusCodes.BAD_REQUEST, {
          message: `buffer is missing/empty`
        });
      }
  
      const Key = `public/static/uploads/${params.mimetype.toLowerCase()}/${uuidv4()}.${Date.now()}.${params.filename}`;
      const Id = `${AppEnvironment.AWS.S3.BUCKET}|${Key}`; // unique id ref for database storage; makes it easy to figure out the bucket and key for later usages/purposes.
      const Link = `${AppEnvironment.AWS.S3.SERVE_ORIGIN}/${Key}`;
      const S3Url = `${AppEnvironment.AWS.S3.S3_URL}/${AppEnvironment.AWS.S3.BUCKET}/${Key}`;
  
      await this.createObject({
        Body: buffer,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: params.mimetype.toLowerCase()
      });
  
      LOGGER.info(`Web link to new upload: ${Link}`);
  
      const results: AwsS3UploadResults = {
        Region: AppEnvironment.AWS.S3.REGION,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: params.mimetype.toLowerCase(),
        Link,
        S3Url,
        Id
      };
  
      LOGGER.info(`AWS S3 upload results:`, { results });
  
      return results;
    }
    catch (error) {
      console.error('s3 error', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
        message: `Could not upload to AWS S3; something went wrong`,
        context: error
      });
    }
  }

  async uploadFile(file: UploadedFile) {
    try {
      if (!file || file.size === 0) {
        throw new HttpRequestException(HttpStatusCodes.BAD_REQUEST, {
          message: `file is missing/empty`
        });
      }
  
      const buffer: Buffer = await readFile(file.tempFilePath);
  
      if (!buffer || buffer.byteLength === 0) {
        throw new HttpRequestException(HttpStatusCodes.BAD_REQUEST, {
          message: `file buffer is missing/empty`
        });
      }
  
      const Key = `public/static/uploads/${file.mimetype.toLowerCase()}/${uuidv4()}.${Date.now()}.${file.name}`;
      const Id = `${AppEnvironment.AWS.S3.BUCKET}|${Key}`; // unique id ref for database storage; makes it easy to figure out the bucket and key for later usages/purposes.
      const Link = `${AppEnvironment.AWS.S3.SERVE_ORIGIN}/${Key}`;
      const S3Url = `${AppEnvironment.AWS.S3.S3_URL}/${AppEnvironment.AWS.S3.BUCKET}/${Key}`;
  
      await this.createObject({
        Body: buffer,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: file.mimetype.toLowerCase()
      });
  
      LOGGER.info(`Web link to new upload: ${Link}`);
  
      const results: AwsS3UploadResults = {
        Region: AppEnvironment.AWS.S3.REGION,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: file.mimetype.toLowerCase(),
        Link,
        S3Url,
        Id
      };
  
      LOGGER.info(`AWS S3 upload results:`, { results });
  
      return results;
    }
    catch (error) {
      console.error('s3 error', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
        message: `Could not upload to AWS S3; something went wrong`,
        context: error
      });
    }
  }

  async uploadFileWithValidation(
    file: string | UploadedFile,
    options?: {
      treatNotFoundAsError: boolean,
      validateAsImage?: boolean,
      mutateObj?: MapType,
      id_prop?: string,
      link_prop?: string;
    }
  ) {
    if (!file) {
      const serviceMethodResults: ServiceMethodResults = {
        status: HttpStatusCodes.BAD_REQUEST,
        error: options && options.hasOwnProperty('treatNotFoundAsError') ? options?.treatNotFoundAsError : true,
        info: {
          message: `No argument found/given`
        }
      };
      
      const errMsg = `AwsS3Service.uploadFile - ${options?.treatNotFoundAsError ? 'error' : 'info'}: no file input...`;
      options?.treatNotFoundAsError
        ? LOGGER.error(errMsg, { options, serviceMethodResults })
        : LOGGER.info(errMsg, { options, serviceMethodResults });
      return serviceMethodResults;
    }

    if (!!options?.validateAsImage && !isImageFileOrBase64(file)) {
      const serviceMethodResults: ServiceMethodResults = {
        status: HttpStatusCodes.BAD_REQUEST,
        error: true,
        info: {
          message: `Bad file input given.`
        }
      };
      return serviceMethodResults;
    }

    try {
      let filepath: string = '';
      let filetype: string = '';
      let filename: string = '';
      let filedata: IUploadFile = null;
      
      if (typeof file === 'string') {
        // base64 string provided; attempt parsing...
        filedata = await upload_base64(file);
        filepath = filedata.file_path;
        filetype = filedata.filetype;
        filename = filedata.filename;
      }
      else {
        filedata = await upload_expressfile(file);
        filetype = (<UploadedFile> file).mimetype;
        filepath = filedata.file_path;
        filename = filedata.filename;
      }

      if (!filetype || !filename || !filepath) {
        throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
          message: `file is missing data`,
          data: { filename, filepath, filetype, file }
        });
      }
  
      const Key = `public/static/uploads/${filetype.toLowerCase()}/${filename}`;
      const Id = `${AppEnvironment.AWS.S3.BUCKET}|${Key}`; // unique id ref for database storage; makes it easy to figure out the bucket and key for later usages/purposes.
      const Link = `${AppEnvironment.AWS.S3.SERVE_ORIGIN}/${Key}`;
      const S3Url = `${AppEnvironment.AWS.S3.S3_URL}/${AppEnvironment.AWS.S3.BUCKET}/${Key}`;

      const Body: Buffer = readFileSync(filepath);

      await this.createObject({
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        Body,
        ContentType: filetype.toLowerCase()
      });

      LOGGER.info(`Web link to new upload: ${Link}`);
  
      const results: AwsS3UploadResults = {
        Region: AppEnvironment.AWS.S3.REGION,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: filetype.toLowerCase(),
        Link,
        S3Url,
        Id
      };

      if (options && options.mutateObj && options.id_prop && options.link_prop) {
        options.mutateObj[options.id_prop] = Id;
        options.mutateObj[options.link_prop] = Link;
      }

      filedata?.remove();
  
      LOGGER.info(`AWS S3 upload results:`, { results });
      const serviceMethodResults: ServiceMethodResults<AwsS3UploadResults> = {
        status: HttpStatusCodes.OK,
        error: false,
        info: {
          data: results
        }
      };
      LOGGER.info(`AWS S3 upload results:`, { results });
      return serviceMethodResults;
    }
    catch (error) {
      const serviceMethodResults: ServiceMethodResults = {
        status: HttpStatusCodes.INTERNAL_SERVER_ERROR,
        error: true,
        info: {
          message: `Could not upload to AWS S3; something went wrong`
        }
      };
      LOGGER.error(serviceMethodResults.info.message || 'Error', { error });
      return serviceMethodResults;
    }
  }

  // create

  async createBucket(Bucket: string) {
    const data = await s3Client.send(new CreateBucketCommand({ Bucket }));
    console.log({ data, Bucket });
    LOGGER.info("Successfully created a bucket called:", { Bucket, data });
    return data; // For unit tests.
  }

  async createObject(params: {
    Bucket: string, // The name of the bucket. For example, 'sample_bucket_101'.
    Key: string, // The name of the object. For example, 'sample_upload.txt'.
    Body: any, // The content of the object. For example, 'Hello world!".
    ContentType: string
  }) {
    const results: PutObjectCommandOutput = await s3Client.send(new PutObjectCommand(params));
    delete params.Body;
    LOGGER.info(
      "Successfully created " +
      params.Key +
      " and uploaded it to " +
      params.Bucket +  "/" + params.Key +
      ", served as ",
      { results, params }
    );
    return results;
  }

  // get

  async getObject(params: {
    Bucket: string // The name of the bucket. For example, 'sample_bucket_101'.
    Key: string, // The name of the object. For example, 'sample_upload.txt'.
  }) {
    const results = await s3Client.send(new GetObjectCommand(params));
    LOGGER.info(
      "Successfully fetched " +
      params.Key +
      " and uploaded it to " +
      params.Bucket +
      "/" +
      params.Key,
      { results, params }
    );
    return results; // For unit tests.
  }

  // delete

  async deleteBucket(Bucket: string) {
    const data = await s3Client.send(new DeleteBucketCommand({ Bucket }));
    LOGGER.info(`Deleted Bucket ${Bucket}`, { data, Bucket });
    return data; // For unit tests.
  }

  async deleteObject(params: {
    Bucket: string, // The name of the bucket. For example, 'sample_bucket_101'.
    Key: string, // The name of the object. For example, 'sample_upload.txt'.
  }) {
    const results = await s3Client.send(new DeleteObjectCommand(params));
    LOGGER.info(
      "Successfully deleted " +
      params.Key +
      " from bucket " +
      params.Bucket,
      { results, params }
    );
    
    return results;
  }


  async bucketExists(Bucket: string): Promise<boolean> {
    try {
      const response = await s3Client.send(new HeadBucketCommand({ Bucket }));
      return true;
    }
    catch {
      return false;
    }
  }
}
''')
  

  
  with open(f"generated-model-resources/repository.service.ts", 'w') as f:
    f.write(''.join(repository_service_contents))

  with open(f"generated-model-resources/openapi.json", 'w') as f:
    f.write(json.dumps(openapi_specs, indent = 2))

  with open(f"common.regex.ts", 'w') as f:
    f.write(regex_contents)

  with open(f"s3.aws.ts", 'w') as f:
    f.write(aws_s3_service)
  


def run():

  convert_models_to_resources()
  
  print("Finished!")
 
  
run()
