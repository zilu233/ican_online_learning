-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: onlinejudgesystem
-- ------------------------------------------------------
-- Server version	5.7.44-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admins` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `User_Name` varchar(50) NOT NULL,
  `PWD` varchar(50) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
INSERT INTO `admins` VALUES (1,'admin','123456');
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `User_Name` varchar(50) DEFAULT NULL,
  `PWD` varchar(50) DEFAULT NULL,
  `Classes` varchar(60) DEFAULT NULL,
  `Name` varchar(50) DEFAULT NULL,
  `Card` varchar(25) DEFAULT NULL,
  `Phone` varchar(20) DEFAULT NULL,
  `Address` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (1,'qqq','123456','大1班','小李','53466888888888888888','13554888888','北京朝阳1区'),(2,'www1','123456','大1班','小红1','564787777777777771','146889888881','南京4区2街道1'),(3,'www','123456','大1班','小智','546888888888888888','15688888456','南京4区街道78'),(4,'eee','123456','大1班','小赵','5321458888954444444','1357888888888','南京4区1街道'),(5,'rrr','123456','大1班','小封','3215548888888888888','+15688888888','南京5区1街道'),(6,'ttt','123456','大1班','小赵','65421478899999999999','135555555555','北京朝阳1区'),(7,'yyy','123456','大1班','啊啊','624622222222222222','136488885411','科黑1区');
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher`
--

DROP TABLE IF EXISTS `teacher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `User_Name` varchar(50) DEFAULT NULL,
  `PWD` varchar(50) DEFAULT NULL,
  `Classes` varchar(60) DEFAULT NULL,
  `Name` varchar(50) DEFAULT NULL,
  `Card` varchar(25) DEFAULT NULL,
  `Phone` varchar(20) DEFAULT NULL,
  `Address` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher`
--

LOCK TABLES `teacher` WRITE;
/*!40000 ALTER TABLE `teacher` DISABLE KEYS */;
INSERT INTO `teacher` VALUES (10,'lilaoshi','123456','','李老师','35555555555555555','1366666666','杭州');
/*!40000 ALTER TABLE `teacher` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test`
--

DROP TABLE IF EXISTS `test`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `test` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `testname` longtext NOT NULL,
  `programetext` int(11) NOT NULL,
  `selecttext` int(11) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test`
--

LOCK TABLES `test` WRITE;
/*!40000 ALTER TABLE `test` DISABLE KEYS */;
INSERT INTO `test` VALUES (1,'小测试',2,2);
/*!40000 ALTER TABLE `test` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_content`
--

DROP TABLE IF EXISTS `test_content`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `test_content` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Content` longtext NOT NULL,
  `Result` longtext NOT NULL,
  `Grade` int(11) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_content`
--

LOCK TABLES `test_content` WRITE;
/*!40000 ALTER TABLE `test_content` DISABLE KEYS */;
INSERT INTO `test_content` VALUES (1,'使用python中的print函数打印出1到10的字符串，1到10之间不能用换行符号。','12345678910',5),(2,'使用print输入下面代码，输出的结果是？\r\nlists = [1,2,3,4]','[1, 2, 3, 4]',5),(3,'一个1-10的数组，长度是多少？','9',5),(4,'一个变量x=[1, 2, 3]的集合，如果x调用insert(1,4)，它的结果是多少，打印出结果。','[1, 4, 2, 3]',8),(5,'一个变量x=[0,1,2,3,4]的集合，如果x调用insert(0,4)，它的结果是多少，打印出结果。','[4, 0, 1, 2, 3, 4]',10),(6,'x的坐标为12，y的坐标是13，求x+y并乘2的结果。','50',2),(7,'使用python中的print函数打印出round(3.1415926,4)结果。','3.1416',5),(8,'a = 15,b=16 使用print函数打印出a > b的结果。','False',5),(9,'计算1到100偶数之间的和是多少？','2550',10),(10,'计算1到100奇数之间的和是多少？','2500',10),(11,'使用len函数获取字符串a=“1234567890”中的长度，并除以2.','5.0',5),(12,'1~100的和是使用python代码并print打印出结果。','5050',5);
/*!40000 ALTER TABLE `test_content` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_record`
--

DROP TABLE IF EXISTS `test_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `test_record` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Students_Id` int(11) DEFAULT NULL,
  `Rocord_Time` datetime DEFAULT NULL,
  `Sum_Grade` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=562 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_record`
--

LOCK TABLES `test_record` WRITE;
/*!40000 ALTER TABLE `test_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_record_answer_content`
--

DROP TABLE IF EXISTS `test_record_answer_content`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `test_record_answer_content` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Test_Record_Id` int(11) NOT NULL,
  `Test_Content_Id` int(11) NOT NULL,
  `Answer_Content` longtext NOT NULL,
  `Grade` int(11) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_record_answer_content`
--

LOCK TABLES `test_record_answer_content` WRITE;
/*!40000 ALTER TABLE `test_record_answer_content` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_record_answer_content` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_record_answer_select`
--

DROP TABLE IF EXISTS `test_record_answer_select`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `test_record_answer_select` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Test_Record_Id` int(11) NOT NULL,
  `Test_Select_Id` int(11) NOT NULL,
  `Answer_Select` varchar(45) NOT NULL,
  `Grade` int(11) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_record_answer_select`
--

LOCK TABLES `test_record_answer_select` WRITE;
/*!40000 ALTER TABLE `test_record_answer_select` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_record_answer_select` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_select`
--

DROP TABLE IF EXISTS `test_select`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `test_select` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Content` longtext NOT NULL,
  `AnswerA` longtext NOT NULL,
  `AnswerB` longtext NOT NULL,
  `AnswerC` longtext NOT NULL,
  `AnswerD` longtext NOT NULL,
  `Result` longtext NOT NULL,
  `Grade` int(11) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_select`
--

LOCK TABLES `test_select` WRITE;
/*!40000 ALTER TABLE `test_select` DISABLE KEYS */;
INSERT INTO `test_select` VALUES (1,'在Java中，以下哪个选项正确地描述了String类的substring方法的功能？','它是一个子串。','它是一个副本。','它是一个视图。','它是额外的内存空间。','A',5),(2,'Java是一种什么语言?','解释型','编译型','面向对象的','动态语言','C',5),(3,' python是一种什么语言?','解释型','编译型','面向对象的','动态语言','A',5),(4,'python中哪个方法用于在控制台上打印输出？','console.log()','print()','display()','output()','B',5),(5,'Java中的异常处理是？','throw','finally-throw','catch-finally-throw','try-catch-finally','D',5),(6,'Java中的异常处理是？','throw','try: pass except : pass','finally','catch-finally-throw','B',5),(7,'以下哪个是 Python 的注释符号?','//','**','#','/**/','C',5),(8,'Python 中定义变量不需要指定数据类型，这是因为 Python 是','静态类型','动态类型','强类型',' 弱类型','B',5),(9,'以下哪个不是 Python 的数据类型',' int','string','float','char','D',5),(10,'表达式 5 // 2 的结果是','2','2.5','3','0','A',5),(11,'以下哪个表达式的结果为 True','5 > 6','5 == 5','5 < 4','5!= 5','B',5),(12,'Python 中字典的键必须是','可变的数据','不可变的数据','整数','字符串','B',5),(13,'以下哪个语句可以用于遍历列表','for i in range (len (list)):','for i in list:','while i < len (list):','both A and B','D',10),(14,'以下哪个是 Python 的内置函数？','sqrt ()','print ()','random ()','math ()','B',5),(15,'在 Python 中，使用（ ）关键字来抛出异常','try','except','raise','finally','C',5),(16,'Python 中，以下哪个模块用于处理日期和时间','time','datetime','calendar','all of the above','D',10),(17,'表达式 \'abc\' * 3 的结果是','\'abcabcabc\'','\'abc3\'','\'3abc\'','报错','A',5),(18,'以下哪个方法可以将字符串中的所有字符转换为大写','lower ','upper ','capitalize ','title ','B',5),(19,'以下哪个模块用于生成随机数','random','math','time','datetime','A',5);
/*!40000 ALTER TABLE `test_select` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-17  1:02:53
