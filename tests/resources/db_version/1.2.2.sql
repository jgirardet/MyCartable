CREATE TABLE "Configuration" (
  "key" TEXT NOT NULL PRIMARY KEY,
  "field" TEXT NOT NULL,
  "str_value" TEXT NOT NULL,
  "int_value" INTEGER,
  "bool_value" BOOLEAN,
  "float_value" REAL,
  "uuid_value" UUID,
  "datetime_value" DATETIME,
  "date_value" DATE,
  "json_value" JSON NOT NULL
);
CREATE TABLE "Utilisateur" (
  "id" UUID NOT NULL PRIMARY KEY,
  "nom" TEXT NOT NULL,
  "prenom" TEXT NOT NULL,
  "last_used" INTEGER
);
CREATE TABLE "Annee" (
  "id" INTEGER NOT NULL PRIMARY KEY,
  "niveau" TEXT NOT NULL,
  "user" UUID NOT NULL REFERENCES "Utilisateur" ("id") ON DELETE CASCADE
);
CREATE INDEX "idx_annee__user" ON "Annee" ("user");
CREATE TABLE "GroupeMatiere" (
  "id" UUID NOT NULL PRIMARY KEY,
  "nom" TEXT NOT NULL,
  "annee" INTEGER NOT NULL REFERENCES "Annee" ("id") ON DELETE CASCADE,
  "_position" INTEGER NOT NULL,
  "_fgColor" INTEGER UNSIGNED NOT NULL,
  "_bgColor" INTEGER UNSIGNED
);
CREATE INDEX "idx_groupematiere__annee" ON "GroupeMatiere" ("annee");
CREATE TABLE "Matiere" (
  "id" UUID NOT NULL PRIMARY KEY,
  "nom" TEXT NOT NULL,
  "groupe" UUID NOT NULL REFERENCES "GroupeMatiere" ("id") ON DELETE CASCADE,
  "_position" INTEGER NOT NULL,
  "_fgColor" INTEGER UNSIGNED NOT NULL,
  "_bgColor" INTEGER UNSIGNED
);
CREATE INDEX "idx_matiere__groupe" ON "Matiere" ("groupe");
CREATE TABLE "Activite" (
  "id" UUID NOT NULL PRIMARY KEY,
  "nom" TEXT NOT NULL,
  "matiere" UUID NOT NULL REFERENCES "Matiere" ("id") ON DELETE CASCADE,
  "_position" INTEGER NOT NULL
);
CREATE INDEX "idx_activite__matiere" ON "Activite" ("matiere");
CREATE TABLE "Page" (
  "id" UUID NOT NULL PRIMARY KEY,
  "created" DATETIME NOT NULL,
  "modified" DATETIME,
  "titre" TEXT NOT NULL,
  "activite" UUID NOT NULL REFERENCES "Activite" ("id") ON DELETE CASCADE,
  "lastPosition" INTEGER
);
CREATE INDEX "idx_page__activite" ON "Page" ("activite");
CREATE TABLE "Section" (
  "id" UUID NOT NULL PRIMARY KEY,
  "created" DATETIME NOT NULL,
  "modified" DATETIME,
  "page" UUID NOT NULL REFERENCES "Page" ("id") ON DELETE CASCADE,
  "_position" INTEGER NOT NULL,
  "classtype" TEXT NOT NULL,
  "path" TEXT,
  "text" TEXT,
  "_datas" TEXT,
  "rows" INTEGER,
  "columns" INTEGER,
  "size" INTEGER,
  "virgule" INTEGER,
  "dividende" TEXT,
  "diviseur" TEXT,
  "quotient" TEXT,
  "content" TEXT,
  "curseur" INTEGER,
  "lignes" INTEGER,
  "colonnes" INTEGER,
  "height" INTEGER,
  "titre" TEXT
);
CREATE INDEX "idx_section__page" ON "Section" ("page");
CREATE TABLE "TableauCell" (
  "x" INTEGER NOT NULL,
  "y" INTEGER NOT NULL,
  "tableau" UUID NOT NULL REFERENCES "Section" ("id") ON DELETE CASCADE,
  "texte" TEXT NOT NULL,
  PRIMARY KEY ("tableau", "y", "x")
);
CREATE TABLE "ZoneFrise" (
  "id" UUID NOT NULL PRIMARY KEY,
  "frise" UUID NOT NULL REFERENCES "Section" ("id") ON DELETE CASCADE,
  "_position" INTEGER NOT NULL,
  "ratio" REAL NOT NULL,
  "texte" TEXT NOT NULL,
  "separatorText" TEXT NOT NULL
);
CREATE INDEX "idx_zonefrise__frise" ON "ZoneFrise" ("frise");
CREATE TABLE "FriseLegende" (
  "id" UUID NOT NULL PRIMARY KEY,
  "texte" TEXT NOT NULL,
  "relativeX" REAL NOT NULL,
  "side" BOOLEAN NOT NULL,
  "zone" UUID NOT NULL REFERENCES "ZoneFrise" ("id") ON DELETE CASCADE
);
CREATE INDEX "idx_friselegende__zone" ON "FriseLegende" ("zone");
CREATE TABLE "Style" (
  "styleId" UUID NOT NULL PRIMARY KEY,
  "_fgColor" INTEGER UNSIGNED NOT NULL,
  "_bgColor" INTEGER UNSIGNED NOT NULL,
  "family" TEXT NOT NULL,
  "underline" BOOLEAN NOT NULL,
  "pointSize" REAL,
  "strikeout" BOOLEAN NOT NULL,
  "weight" INTEGER,
  "tableau_cell_tableau" UUID,
  "tableau_cell_y" INTEGER,
  "tableau_cell_x" INTEGER,
  "zone_frise" UUID REFERENCES "ZoneFrise" ("id") ON DELETE CASCADE,
  FOREIGN KEY ("tableau_cell_tableau", "tableau_cell_y", "tableau_cell_x") REFERENCES "TableauCell" ("tableau", "y", "x") ON DELETE CASCADE
);
CREATE INDEX "idx_style__tableau_cell_tableau_tableau_cell_y_tableau_cell_x" ON "Style" ("tableau_cell_tableau", "tableau_cell_y", "tableau_cell_x");
CREATE INDEX "idx_style__zone_frise" ON "Style" ("zone_frise");
CREATE TABLE "Annotation" (
  "id" UUID NOT NULL PRIMARY KEY,
  "x" REAL NOT NULL,
  "y" REAL NOT NULL,
  "section" UUID NOT NULL REFERENCES "Section" ("id") ON DELETE CASCADE,
  "style" UUID REFERENCES "Style" ("styleId") ON DELETE SET NULL,
  "classtype" TEXT NOT NULL,
  "text" TEXT,
  "width" REAL,
  "height" REAL,
  "tool" TEXT,
  "startX" REAL,
  "startY" REAL,
  "endX" REAL,
  "endY" REAL
);
CREATE INDEX "idx_annotation__section" ON "Annotation" ("section");
CREATE INDEX "idx_annotation__style" ON "Annotation" ("style")
