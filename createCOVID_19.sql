-- -----------------------------------------------------------------------------
--
-- COVID_19 Database
-- 
-- 
-- Clean out the old teefile; likely this command is system specific
\! rm -f covid19_db_creation-outfile.txt
tee covid19_db_creation-outfile.txt;
-- Show warnings after every statement
warnings;
drop 
  database if exists COVID_19;
create database if not exists COVID_19;
use COVID_19;
drop 
  table if exists PopulationResults;
drop 
  table if exists RelevantFactorsResults;
drop 
  table if exists PatientDescriptionsResults;
drop 
  table if exists ModelsOpenQuestionsResults;
drop 
  table if exists MaterialsResults;
drop 
  table if exists DiagnosticsResults;
drop 
  table if exists TherapeuticInterventionsResults;
drop 
  table if exists RiskFactorResults;
drop 
  table if exists RiskFactor;
drop 
  table if exists SeverityResults;
drop 
  table if exists FatalityResults;
drop 
  table if exists MultivariateAdjustments;
drop 
  table if exists MeasuresOfEvidence;
drop 
  table if exists DaysAfterOnset;
drop 
  table if exists Study;
drop 
  table if exists Journal;
-- PopulationResults ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create PopulationResults' as '';
create table PopulationResults (
  resultID char(12) not null, 
  studyName char(251) not null, 
  datePublished date, 
  studyType char(35), 
  journalName varchar(166), 
  studyLink varchar(290) not null, 
  addressed char(78) not null, 
  challenge varchar(475), 
  solution varchar(1266) not null, 
  -- Key Constraints
  primary key (resultID)
);
load data infile '/var/lib/mysql-files/output/1_population.csv' ignore into table PopulationResults fields terminated by ',' enclosed by '"' lines terminated by '\n' ignore 1 lines (
  @throwaway, datePublished, studyName, 
  studyLink, journalName, resultID, 
  studyType, addressed, challenge, 
  solution, @throwaway, @throwaway
);
-- RelevantFactorsResults ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create RelevantFactorsResults' as '';
create table RelevantFactorsResults (
  resultID char(12) not null, 
  studyName char(251) not null, 
  datePublished date, 
  studyType char(35), 
  journalName varchar(166), 
  studyLink varchar(290) not null, 
  factors char(186) not null, 
  influential char(1), 
  excerpt varchar(1551) not null, 
  -- Key Constraints
  primary key (resultID),
  check (influential = 'Y' OR influential = 'N')
);
load data infile '/var/lib/mysql-files/output/2_relevant_factors.csv' ignore into table RelevantFactorsResults fields terminated by ',' enclosed by '"' lines terminated by '\n' ignore 1 lines (
  @throwaway, datePublished, studyName, 
  studyLink, journalName, resultID, 
  studyType, factors, influential, 
  excerpt, @throwaway, @throwaway
);
-- PatientDescriptionsResults ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create PatientDescriptionsResults' as '';
create table PatientDescriptionsResults (
  resultID char(12) not null, 
  studyName char(251) not null, 
  datePublished date, 
  studyType char(35), 
  journalName varchar(166), 
  studyLink varchar(290) not null, 
  sampleSize char(255) not null, 
  age char(88), 
  sampleObtained char(47), 
  asymptomatic decimal(65, 30) not null, 
  excerpt varchar(1551) not null, 
  viralLoadSample char(1), 
  -- Key Constraints
  primary key (resultID),
  check (asymptomatic >= 0 AND asymptomatic <= 1),
  check (viralLoadSample = 'Y' OR viralLoadSample = 'N')
);
load data infile '/var/lib/mysql-files/output/3_patient_descriptions.csv' ignore into table PatientDescriptionsResults fields terminated by ',' enclosed by '"' lines terminated by '\n' ignore 1 lines (
  @throwaway, datePublished, studyName, 
  studyLink, journalName, resultID, 
  studyType, sampleSize, @age, @sampleObtained, 
  asymptomatic, excerpt, viralLoadSample
) 
set 
  age = if(@age like '-%', NULL, @age), 
  sampleObtained = if(
    @sampleObtained like '-%', NULL, @sampleObtained
  );
-- ModelsOpenQuestionsResults ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create ModelsOpenQuestionsResults' as '';
create table ModelsOpenQuestionsResults (
  resultID char(12) not null, 
  studyName char(251) not null, 
  datePublished date, 
  studyType char(35), 
  journalName varchar(166), 
  studyLink varchar(290) not null, 
  method char(155), 
  excerpt varchar(1551) not null, 
  -- Key Constraints
  primary key (resultID)
);
load data infile '/var/lib/mysql-files/output/4_models_and_open_questions.csv' ignore into table ModelsOpenQuestionsResults fields terminated by ',' enclosed by '"' lines terminated by '\n' ignore 1 lines (
  @throwaway, datePublished, studyName, 
  studyLink, journalName, resultID, 
  @method, excerpt, @throwaway, studyType
) 
set 
  method = if(
    @method like '-%' 
    or @method like '', 
    NULL, 
    @method
  ), 
  studyType = if(
    @studyType like '', NULL, @studyType
  );
-- MaterialsResults ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create MaterialsResults' as '';
create table MaterialsResults (
  resultID char(12) not null, 
  studyName char(251) not null, 
  datePublished date, 
  studyType char(35), 
  journalName varchar(166), 
  studyLink varchar(290) not null, 
  material char(14) not null, 
  method char(155) not null, 
  conclusion varchar(727) not null, 
  patientSeverity char(24), 
  -- Key Constraints
  primary key (resultID)
);
load data infile '/var/lib/mysql-files/output/5_materials.csv' ignore into table MaterialsResults fields terminated by ',' enclosed by '"' lines terminated by '\n' ignore 1 lines (
  @throwaway, datePublished, studyName, 
  studyLink, journalName, resultID, 
  studyType, material, method, @throwaway, 
  conclusion, @throwaway, @patientSeverity, 
  @throwaway
) 
set 
  patientSeverity = if(
    @patientSeverity like '-%', NULL, @patientSeverity
  );
-- DiagnosticsResults ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create DiagnosticsResults' as '';
create table DiagnosticsResults (
  resultID char(12) not null, 
  studyName char(226) not null, 
  datePublished date, 
  studyType char(35), 
  journalName varchar(166), 
  studyLink varchar(290) not null, 
  detectionMethod char(70) not null, 
  sampleSize char(255), 
  testingAccuracy varchar(465), 
  assaySpeed varchar(500), 
  fdaApproval char(255), 
  -- Key Constraints
  primary key (resultID)
);
load data infile '/var/lib/mysql-files/output/6_diagnostics.csv' ignore into table DiagnosticsResults fields terminated by ',' enclosed by '"' lines terminated by '\n' ignore 1 lines (
  @throwaway, @datePublished, studyName, 
  studyLink, journalName, resultID, 
  detectionMethod, @sampleSize, @testingAccuracy, 
  @assaySpeed, @fdaApproval, studyType
) 
set 
  datePublished = if(
    @datePublished like '', NULL, @datePublished
  ), 
  sampleSize = if(
    @sampleSize like '-%' 
    or @sampleSize like '', 
    NULL, 
    @sampleSize
  ), 
  testingAccuracy = if(
    @testingAccuracy like '-%', NULL, @testingAccuracy
  ), 
  assaySpeed = if(
    @assaySpeed like '-%' 
    or @assaySpeed like '', 
    NULL, 
    @assaySpeed
  ), 
  fdaApproval = if(
    @fdaApproval like '-%', NULL, @fdaApproval
  );
-- TherapeuticInterventionsResults ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create TherapeuticInterventionsResults' as '';
create table TherapeuticInterventionsResults (
  resultID char(12) not null, 
  studyName char(251) not null, 
  datePublished date, 
  studyType char(35), 
  journalName varchar(166), 
  studyLink varchar(290) not null, 
  therapeuticMethod varchar(495) not null, 
  sampleSize char(67), 
  diseaseSeverity varchar(419), 
  generalOutcome varchar(1521) not null, 
  primaryEndpoint varchar(1611), 
  clinicalImprovement char(1), 
  -- Key Constraints
  primary key (resultID),
  check (clinicalImprovement = 'Y' OR clinicalImprovement = 'N')
);
load data infile '/var/lib/mysql-files/output/7_therapeutics_interventions_and_clinical_studies.csv' ignore into table TherapeuticInterventionsResults fields terminated by ',' enclosed by '"' lines terminated by '\n' ignore 1 lines (
  @throwaway, datePublished, studyName, 
  studyLink, journalName, resultID, 
  therapeuticMethod, @sampleSize, 
  @diseaseSeverity, generalOutcome, 
  @primaryEndpoint, @clinicalImprovement, 
  @studyType, @throwaway
) 
set 
  sampleSize = if(
    @sampleSize like '-%', NULL, @sampleSize
  ), 
  diseaseSeverity = if(
    @diseaseSeverity like '-%', NULL, @diseaseSeverity
  ), 
  primaryEndpoint = if(
    @primaryEndpoint like '-%', NULL, @primaryEndpoint
  ), 
  clinicalImprovement = if(
    @clinicalImprovement like '-%', NULL, 
    @clinicalImprovement
  ), 
  studyType = if(
    @studyType like '-%', NULL, @studyType
  );
-- RiskFactorResults ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create RiskFactorResults' as '';
create table RiskFactorResults (
  resultID char(12) not null, 
  studyName char(251) not null, 
  datePublished date, 
  studyType char(35), 
  journalName varchar(166), 
  studyLink varchar(290) not null, 
  riskFactorName char(35) not null, 
  sampleSize char(64) not null, 
  studyPopulation varchar(556) not null, 
  criticalOnly char(1) not null, 
  dvd char(1) not null, 
  severity char(27), 
  severityLowerBound decimal(3, 2), 
  severityUpperBound decimal(4, 2), 
  severitypValue char(5), 
  severitySignificance char(15), 
  severityAdjusted char(22), 
  severityCalculated char(22), 
  fatality char(35), 
  fatalityLowerBound decimal(4, 2), 
  fatalityUpperBound decimal(5, 2), 
  fatalitypValue char(5), 
  fatalitySignificance char(15), 
  fatalityAdjusted char(12), 
  fatalityCalculated char(27), 
  -- Key Constraints
  primary key (resultID),
  check (dvd = 'Y' OR dvd = 'N'),
  check (criticalOnly = 'Y' OR criticalOnly = 'N')
);
load data infile '/var/lib/mysql-files/output/8_risk_factors.csv' ignore into table RiskFactorResults fields terminated by ',' enclosed by '"' lines terminated by '\n' ignore 1 lines (
  @throwaway, datePublished, studyName, 
  studyLink, journalName, resultID, 
  @severity, @severityLowerBound, 
  @severityUpperBound, @severitypValue, 
  @severitySignificance, @severityAdjusted, 
  @severityCalculated, @fatality, 
  @fatalityLowerBound, @fatalityUpperBound, 
  @fatalitypValue, @fatalitySignificance, 
  @fatalityAdjusted, @fatalityCalculated, 
  @throwaway, studyType, sampleSize, 
  studyPopulation, criticalOnly, dvd, 
  riskFactorName
) 
set 
  severity = if(@severity like '', NULL, @severity), 
  severityLowerBound = if(
    @severityLowerBound like '', NULL, 
    @severityLowerBound
  ), 
  severityUpperBound = if(
    @severityUpperBound like '', NULL, 
    @severityUpperBound
  ), 
  severitypValue = if(
    @severitypValue like '', NULL, @severitypValue
  ), 
  severitySignificance = if(
    @severitySignificance like '', NULL, 
    @severitySignificance
  ), 
  severityAdjusted = if(
    @severityAdjusted like '', NULL, @severityAdjusted
  ), 
  severityCalculated = if(
    @severityCalculated like '', NULL, 
    @severityCalculated
  ), 
  fatality = if(@fatality like '', NULL, @fatality), 
  fatalityLowerBound = if(
    @fatalityLowerBound like '', NULL, 
    @fatalityLowerBound
  ), 
  fatalityUpperBound = if(
    @fatalityUpperBound like '', NULL, 
    @fatalityUpperBound
  ), 
  fatalitypValue = if(
    @fatalitypValue like '', NULL, @fatalitypValue
  ), 
  fatalitySignificance = if(
    @fatalitySignificance like '', NULL, 
    @fatalitySignificance
  ), 
  fatalityAdjusted = if(
    @fatalityAdjusted like '', NULL, @fatalityAdjusted
  ), 
  fatalityCalculated = if(
    @fatalityCalculated like '', NULL, 
    @fatalityCalculated
  );
-- RiskFactor ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create RiskFactor' as '';
create table RiskFactor (
  studyName char(251) not null, 
  riskFactorName char(35) not null, 
  -- Key Constraints
  primary key (studyName, riskFactorName)
);
insert into RiskFactor 
select 
  distinct studyName, 
  riskFactorName 
from 
  RiskFactorResults;
-- SeverityResults ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create SeverityResults' as '';
create table SeverityResults (
  resultID char(12) not null, 
  studyName char(251) not null, 
  riskFactorName char(35) not null, 
  severity char(27), 
  severityLowerBound decimal(3, 2), 
  severityUpperBound decimal(4, 2), 
  severitypValue char(5), 
  severitySignificance char(15), 
  severityAdjusted char(22), 
  severityCalculated char(22), 
  -- Key Constraints
  primary key (
    studyName, resultID, riskFactorName
  ),
  check(severityLowerBound <= severityUpperBound)
);
insert into SeverityResults 
select 
  distinct resultID, 
  studyName, 
  riskFactorName, 
  severity, 
  severityLowerBound, 
  severityUpperBound, 
  severitypValue, 
  severitySignificance, 
  severityAdjusted, 
  severityCalculated 
from 
  RiskFactorResults;
-- FatalityResults ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create FatalityResults' as '';
create table FatalityResults (
  resultID char(12) not null, 
  studyName char(251) not null, 
  riskFactorName char(35) not null, 
  fatality char(35), 
  fatalityLowerBound decimal(4, 2), 
  fatalityUpperBound decimal(5, 2), 
  fatalitypValue char(5), 
  fatalitySignificance char(15), 
  fatalityAdjusted char(12), 
  fatalityCalculated char(27), 
  -- Key Constraints
  primary key (
    studyName, resultID, riskFactorName
  )
);
insert into FatalityResults 
select 
  distinct resultID, 
  studyName, 
  riskFactorName, 
  fatality, 
  fatalityLowerBound, 
  fatalityUpperBound, 
  fatalitypValue, 
  fatalitySignificance, 
  fatalityAdjusted, 
  fatalityCalculated 
from 
  RiskFactorResults;
-- MultivariateAdjustments ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create MultivariateAdjustments' as '';
create table MultivariateAdjustments (
  resultID char(12) not null, 
  studyName char(251) not null, 
  adjustment char(66) not null, 
  -- Key Constraints
  primary key (resultID, adjustment)
);
load data infile '/var/lib/mysql-files/output/multivaradjustments.csv' ignore into table MultivariateAdjustments fields terminated by ',' enclosed by '"' lines terminated by '\n' ignore 1 lines (
  @throwaway, studyName, resultID, adjustment
);
-- MeasuresOfEvidence ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create MeasuresOfEvidence' as '';
create table MeasuresOfEvidence (
  resultID char(12) not null, 
  studyName char(251) not null, 
  measureType char(30) not null, 
  measureData char(159) not null, 
  -- Key Constraints
  primary key (resultID, measureType)
);
load data infile '/var/lib/mysql-files/output/measures.csv' ignore into table MeasuresOfEvidence fields terminated by ',' enclosed by '"' lines terminated by '\n' ignore 1 lines (
  @throwaway, studyName, resultID, measureType, 
  measureData
);
-- DaysAfterOnset ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create DaysAfterOnset' as '';
create table DaysAfterOnset (
  resultID char(12) not null, 
  studyName char(251) not null, 
  resultType char(6) not null, 
  daysValue char(11) not null, 
  -- Key Constraints
  primary key (resultID, resultType)
);
load data infile '/var/lib/mysql-files/output/daysafteronset.csv' ignore into table DaysAfterOnset fields terminated by ',' enclosed by '"' lines terminated by '\n' ignore 1 lines (
  @throwaway, studyName, resultID, resultType, 
  daysValue
);
-- Study ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create Study' as '';
create table Study (
  studyName char(251) not null, 
  datePublished date, 
  studyType char(35), 
  journalName varchar(166), 
  studyLink varchar(290) not null -- Key Constraints
  );

-- Pull in all studies from various result types
insert into Study 
select 
  distinct studyName, 
  datePublished, 
  studyType, 
  journalName, 
  studyLink 
from 
  PopulationResults;
insert into Study 
select 
  distinct studyName, 
  datePublished, 
  studyType, 
  journalName, 
  studyLink 
from 
  RelevantFactorsResults;
insert into Study 
select 
  distinct studyName, 
  datePublished, 
  studyType, 
  journalName, 
  studyLink 
from 
  PatientDescriptionsResults;
insert into Study 
select 
  distinct studyName, 
  datePublished, 
  studyType, 
  journalName, 
  studyLink 
from 
  ModelsOpenQuestionsResults;
insert into Study 
select 
  distinct studyName, 
  datePublished, 
  studyType, 
  journalName, 
  studyLink 
from 
  MaterialsResults;
insert into Study 
select 
  distinct studyName, 
  datePublished, 
  studyType, 
  journalName, 
  studyLink 
from 
  DiagnosticsResults;
insert into Study 
select 
  distinct studyName, 
  datePublished, 
  studyType, 
  journalName, 
  studyLink 
from 
  TherapeuticInterventionsResults;
insert into Study 
select 
  distinct studyName, 
  datePublished, 
  studyType, 
  journalName, 
  studyLink 
from 
  RiskFactorResults;

-- Get rid of duplicates
alter table 
  Study 
add 
  studyID int primary key auto_increment;
delete t1 
from 
  Study as t1, 
  Study as t2 
where 
  t1.studyID > t2.studyID 
  and t1.studyName = t2.studyName;
alter table 
  Study modify studyID int not null;
alter table 
  Study 
drop 
  primary key;

-- Add proper primary key now that duplicates have been dropped
alter table 
  Study 
add 
  primary key(studyName);
-- Journal ------------------------------------------------------------------------
select 
  '-----------------------------------------------------------------' as '';
select 
  'Create Journal' as '';
create table Journal (
  journalName varchar(166) not null, 
  -- Key Constraints
  primary key (journalName)
);
insert into Journal 
select 
  distinct journalName 
from 
  Study;

  -- Drop non-result-specific details from each result type schema
alter table 
  PopulationResults 
drop 
  datePublished, 
drop 
  studyType, 
drop 
  journalName, 
drop 
  studyLink;
alter table 
  RelevantFactorsResults 
drop 
  datePublished, 
drop 
  studyType, 
drop 
  journalName, 
drop 
  studyLink;
alter table 
  PatientDescriptionsResults 
drop 
  datePublished, 
drop 
  studyType, 
drop 
  journalName, 
drop 
  studyLink;
alter table 
  ModelsOpenQuestionsResults 
drop 
  datePublished, 
drop 
  studyType, 
drop 
  journalName, 
drop 
  studyLink;
alter table 
  MaterialsResults 
drop 
  datePublished, 
drop 
  studyType, 
drop 
  journalName, 
drop 
  studyLink;
alter table 
  DiagnosticsResults 
drop 
  datePublished, 
drop 
  studyType, 
drop 
  journalName, 
drop 
  studyLink;
alter table 
  TherapeuticInterventionsResults 
drop 
  datePublished, 
drop 
  studyType, 
drop 
  journalName, 
drop 
  studyLink;
alter table 
  RiskFactorResults 
drop 
  datePublished, 
drop 
  studyType, 
drop 
  journalName, 
drop 
  studyLink, 
drop 
  severity, 
drop 
  severityLowerBound, 
drop 
  severityUpperBound, 
drop 
  severitypValue, 
drop 
  severitySignificance, 
drop 
  severityAdjusted, 
drop 
  severityCalculated, 
drop 
  fatality, 
drop 
  fatalityLowerBound, 
drop 
  fatalityUpperBound, 
drop 
  fatalitypValue, 
drop 
  fatalitySignificance, 
drop 
  fatalityAdjusted, 
drop 
  fatalityCalculated;

-- Setup studyName foreign keys
alter table 
  PopulationResults 
add 
  constraint studyName_fk1 foreign key (studyName) references Study(studyName);
alter table 
  RelevantFactorsResults 
add 
  constraint studyName_fk2 foreign key (studyName) references Study(studyName);
alter table 
  PatientDescriptionsResults 
add 
  constraint studyName_fk3 foreign key (studyName) references Study(studyName);
alter table 
  ModelsOpenQuestionsResults 
add 
  constraint studyName_fk4 foreign key (studyName) references Study(studyName);
alter table 
  MaterialsResults 
add 
  constraint studyName_fk5 foreign key (studyName) references Study(studyName);
alter table 
  DiagnosticsResults 
add 
  constraint studyName_fk6 foreign key (studyName) references Study(studyName);
alter table 
  TherapeuticInterventionsResults 
add 
  constraint studyName_fk7 foreign key (studyName) references Study(studyName);
alter table 
  RiskFactorResults 
add 
  constraint studyName_fk8 foreign key (studyName) references Study(studyName);

-- Add index to riskFactorResults type
create index idxRiskFactor on RiskFactorResults(studyName, riskFactorName);
create index idxRiskFactorResults on RiskFactorResults(
  studyName, resultID, riskFactorName
);
alter table 
  RiskFactor 
add 
  constraint riskFactor_fk1 foreign key (studyName, riskFactorName) references RiskFactorResults(studyName, riskFactorName);
-- Add foreign key constraints to result-specific types (
alter table 
  SeverityResults 
add 
  constraint riskFactor_fk2 foreign key (
    studyName, resultID, riskFactorName
  ) references RiskFactorResults(
    studyName, resultID, riskFactorName
  );
alter table 
  FatalityResults 
add 
  constraint riskFactor_fk3 foreign key (
    studyName, resultID, riskFactorName
  ) references RiskFactorResults(
    studyName, resultID, riskFactorName
  );
create index idxStudy on Study(journalName);
alter table 
  Journal 
add 
  constraint journalName_fk1 foreign key (journalName) references Study(journalName);
-- Finish
nowarning;
notee;
