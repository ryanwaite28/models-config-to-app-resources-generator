export const S3Object = sequelize.define("user_tags", {
  id: { type: DataTypes.INTEGER, allowNull: false, primaryKey: true, autoIncrement: true },
  metadata: { type: DataTypes.JSONB, allowNull: true },
  create_at: { type: DataTypes.DATETIME, allowNull: false },
  updated_at: { type: DataTypes.DATETIME, allowNull: true },
  deleted_at: { type: DataTypes.DATETIME, allowNull: true },
  model_type: { type: DataTypes.STRING, allowNull: true },
  model_id: { type: DataTypes.INTEGER, allowNull: true },
  mimetype: { type: DataTypes.STRING, allowNull: true },
  is_private: { type: DataTypes.BOOLEAN, allowNull: false },
  region: { type: DataTypes.STRING, allowNull: false },
  bucket: { type: DataTypes.STRING, allowNull: false },
  key: { type: DataTypes.STRING, allowNull: false },
});
  

export const User = sequelize.define("user_tags", {
  id: { type: DataTypes.INTEGER, allowNull: false, primaryKey: true, autoIncrement: true },
  metadata: { type: DataTypes.JSONB, allowNull: true },
  create_at: { type: DataTypes.DATETIME, allowNull: false },
  updated_at: { type: DataTypes.DATETIME, allowNull: true },
  deleted_at: { type: DataTypes.DATETIME, allowNull: true },
  stripe_customer_account_id: { type: DataTypes.STRING, allowNull: true },
  stripe_account_id: { type: DataTypes.STRING, allowNull: true },
  stripe_account_verified: { type: DataTypes.BOOLEAN, allowNull: false },
  stripe_identity_verified: { type: DataTypes.BOOLEAN, allowNull: false },
  first_name: { type: DataTypes.STRING, allowNull: true },
  last_name: { type: DataTypes.STRING, allowNull: true },
  bio: { type: DataTypes.STRING, allowNull: true },
  icon_s3object_id: { type: DataTypes.INTEGER, allowNull: true },
  town: { type: DataTypes.STRING, allowNull: true },
  city: { type: DataTypes.STRING, allowNull: true },
  state: { type: DataTypes.STRING, allowNull: true },
  zipcode: { type: DataTypes.INTEGER, allowNull: true },
  country: { type: DataTypes.STRING, allowNull: true },
  tags: { type: DataTypes.TEXT, allowNull: true },
  specialties: { type: DataTypes.TEXT, allowNull: true },
  person_verified: { type: DataTypes.BOOLEAN, allowNull: false },
  email_verified: { type: DataTypes.BOOLEAN, allowNull: false },
  phone_verified: { type: DataTypes.BOOLEAN, allowNull: false },
});
  

export const UserAuthProvider = sequelize.define("user_tags", {
  id: { type: DataTypes.INTEGER, allowNull: false, primaryKey: true, autoIncrement: true },
  metadata: { type: DataTypes.JSONB, allowNull: true },
  create_at: { type: DataTypes.DATETIME, allowNull: false },
  updated_at: { type: DataTypes.DATETIME, allowNull: true },
  deleted_at: { type: DataTypes.DATETIME, allowNull: true },
  details: { type: DataTypes.JSONB, allowNull: true },
  user_id: { type: DataTypes.INTEGER, allowNull: false },
  provider_name: { type: DataTypes.STRING, allowNull: false },
  provider_id: { type: DataTypes.STRING, allowNull: false },
});
  

export const Tag = sequelize.define("user_tags", {
  id: { type: DataTypes.INTEGER, allowNull: false, primaryKey: true, autoIncrement: true },
  metadata: { type: DataTypes.JSONB, allowNull: true },
  create_at: { type: DataTypes.DATETIME, allowNull: false },
  updated_at: { type: DataTypes.DATETIME, allowNull: true },
  deleted_at: { type: DataTypes.DATETIME, allowNull: true },
  name: { type: DataTypes.STRING, allowNull: false },
  description: { type: DataTypes.TEXT, allowNull: true },
});
  

export const UserTag = sequelize.define("user_tags", {
  id: { type: DataTypes.INTEGER, allowNull: false, primaryKey: true, autoIncrement: true },
  metadata: { type: DataTypes.JSONB, allowNull: true },
  create_at: { type: DataTypes.DATETIME, allowNull: false },
  updated_at: { type: DataTypes.DATETIME, allowNull: true },
  deleted_at: { type: DataTypes.DATETIME, allowNull: true },
  user_id: { type: DataTypes.INTEGER, allowNull: false },
  tag_id: { type: DataTypes.INTEGER, allowNull: false },
});
  

User.hasOne(S3Object, { as: "icon", foreignKey: "id", sourceKey: "icon_s3object_id" });

User.hasMany(UserAuthProvider, { as: "authProviders", foreignKey: "user_id", sourceKey: "id" });

User.hasMany(Tag, { as: "user_tags", foreignKey: "user_id", sourceKey: "id" });

UserAuthProvider.belongsTo(User, { as: "user", foreignKey: "user_id", targetKey: "id" });

Tag.belongsToMany(User, { as: "users", foreignKey: "user_id", targetKey: "id" });

UserTag.belongsTo(User, { as: "user", foreignKey: "user_id", targetKey: "id" });

UserTag.belongsTo(Tag, { as: "tag", foreignKey: "tag_id", targetKey: "id" });