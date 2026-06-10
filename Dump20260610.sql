-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: mall_management_system
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Table structure for table `bill`
--

DROP TABLE IF EXISTS `bill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bill` (
  `Bill_ID` int NOT NULL,
  `Bill_Date` date NOT NULL,
  `Bill_Time` time NOT NULL,
  `Total_Amount` decimal(10,2) DEFAULT NULL,
  `Discount` decimal(10,2) DEFAULT NULL,
  `Final_Amount` decimal(10,2) DEFAULT NULL,
  `Customer_ID` int NOT NULL,
  `Shop_ID` int NOT NULL,
  `SSN` varchar(20) NOT NULL,
  PRIMARY KEY (`Bill_ID`),
  KEY `Shop_ID` (`Shop_ID`),
  KEY `idx_bill_date` (`Bill_Date`),
  KEY `idx_bill_customer` (`Customer_ID`),
  KEY `idx_bill_employee` (`SSN`),
  CONSTRAINT `bill_ibfk_1` FOREIGN KEY (`Customer_ID`) REFERENCES `customer` (`Customer_ID`),
  CONSTRAINT `bill_ibfk_2` FOREIGN KEY (`Shop_ID`) REFERENCES `shop` (`Shop_ID`),
  CONSTRAINT `bill_ibfk_3` FOREIGN KEY (`SSN`) REFERENCES `employee` (`SSN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bill`
--

LOCK TABLES `bill` WRITE;
/*!40000 ALTER TABLE `bill` DISABLE KEYS */;
INSERT INTO `bill` VALUES (130,'2026-04-09','02:37:11',2000.00,0.00,2000.00,301,101,'SSN001'),(140,'2026-04-09','02:35:21',2000.00,0.00,2000.00,301,101,'SSN001'),(501,'2025-01-20','18:30:00',70000.00,1200.00,55000.00,302,102,'SSN002'),(502,'2025-01-21','14:10:00',70000.00,200.00,1800.00,301,101,'SSN001'),(503,'2025-01-21','16:45:00',32000.00,2000.00,30000.00,303,104,'SSN004'),(504,'2025-01-22','13:20:00',5500.00,500.00,5000.00,304,103,'SSN003'),(505,'2025-01-22','19:05:00',499.00,0.00,499.00,306,105,'SSN006'),(506,'2025-01-23','17:40:00',4300.00,300.00,4000.00,305,101,'SSN001'),(507,'2026-03-19','01:52:20',60000.00,1000.00,59000.00,302,102,'SSN002'),(508,'2026-03-19','02:00:34',7996.00,0.00,7996.00,304,103,'SSN003'),(509,'2026-03-19','02:29:09',1999.00,23.00,1976.00,305,103,'SSN005'),(510,'2026-03-19','04:39:18',3998.00,23.00,3078.46,303,103,'SSN003'),(511,'2026-03-19','04:40:02',3998.00,23.00,3078.46,303,103,'SSN003'),(512,'2026-03-19','04:40:56',3998.00,23.00,3078.46,303,103,'SSN005'),(513,'2026-03-19','04:42:01',1999.00,23.00,1539.23,303,103,'SSN005'),(514,'2026-03-19','04:42:38',6998.00,12.00,6158.24,305,101,'SSN001'),(515,'2026-03-19','04:43:12',55000.00,12.00,48400.00,305,102,'SSN002'),(516,'2026-03-19','05:41:53',998.00,12.00,878.24,303,105,'SSN006'),(517,'2026-03-19','06:05:51',998.00,0.00,998.00,307,105,'SSN006'),(518,'2026-03-19','10:50:35',55000.00,13.00,47850.00,303,102,'SSN002'),(519,'2026-03-19','12:04:35',1999.00,0.00,1999.00,307,103,'SSN005'),(520,'2026-03-19','13:18:43',60000.00,25.00,45000.00,302,104,'SSN004'),(521,'2026-03-19','14:03:59',1999.00,25.00,1499.25,303,103,'SSN003'),(522,'2026-03-19','14:08:49',3998.00,25.00,2998.50,304,103,'SSN005'),(523,'2026-04-08','05:01:11',2500.00,10.00,2250.00,301,101,'SSN001'),(531,'2026-04-08','17:25:22',2500.00,10.00,2250.00,301,101,'SSN001'),(540,'2026-04-08','17:24:49',2000.00,0.00,2000.00,301,101,'SSN001'),(580,'2026-04-09','01:01:58',9999.00,0.00,9999.00,302,102,'SSN002'),(583,'2026-04-08','05:15:10',2500.00,10.00,2250.00,301,101,'SSN001'),(591,'2026-04-08','05:16:27',2500.00,10.00,2250.00,301,101,'SSN001'),(592,'2026-04-08','05:40:50',150000.00,45.00,82500.00,303,102,'SSN002'),(631,'2026-04-08','23:52:10',2500.00,10.00,2250.00,301,101,'SSN001'),(682,'2026-04-09','14:16:06',2500.00,10.00,2250.00,301,101,'SSN001'),(692,'2026-04-09','14:26:53',2500.00,10.00,2250.00,301,101,'SSN001'),(1040,'2026-04-09','02:33:14',2000.00,0.00,2000.00,301,101,'SSN001'),(1240,'2026-04-09','13:15:34',2000.00,0.00,2000.00,301,101,'SSN001'),(8040,'2026-04-09','14:30:31',2000.00,0.00,2000.00,301,101,'SSN001'),(8041,'2026-04-18','19:46:44',5997.00,10.00,5397.30,305,103,'SSN005'),(8042,'2026-04-18','19:58:41',3998.00,10.00,3598.20,303,103,'SSN005'),(8043,'2026-04-18','20:00:12',1999.00,10.00,1799.10,305,103,'SSN003'),(8044,'2026-04-18','20:03:56',2500.00,10.00,2250.00,304,103,'SSN005'),(8045,'2026-04-18','20:13:33',1999.00,10.00,1799.10,303,103,'SSN005');
/*!40000 ALTER TABLE `bill` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `bill_details`
--

DROP TABLE IF EXISTS `bill_details`;
/*!50001 DROP VIEW IF EXISTS `bill_details`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `bill_details` AS SELECT 
 1 AS `Bill_ID`,
 1 AS `Customer_Name`,
 1 AS `Shop_Name`,
 1 AS `Final_Amount`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `bill_item`
--

DROP TABLE IF EXISTS `bill_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bill_item` (
  `Bill_ID` int NOT NULL,
  `Item_ID` int NOT NULL,
  `Quantity` int DEFAULT NULL,
  PRIMARY KEY (`Bill_ID`,`Item_ID`),
  KEY `Item_ID` (`Item_ID`),
  CONSTRAINT `bill_item_ibfk_1` FOREIGN KEY (`Bill_ID`) REFERENCES `bill` (`Bill_ID`) ON DELETE CASCADE,
  CONSTRAINT `bill_item_ibfk_2` FOREIGN KEY (`Item_ID`) REFERENCES `item` (`Item_ID`),
  CONSTRAINT `bill_item_chk_1` CHECK ((`Quantity` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bill_item`
--

LOCK TABLES `bill_item` WRITE;
/*!40000 ALTER TABLE `bill_item` DISABLE KEYS */;
INSERT INTO `bill_item` VALUES (501,402,1),(502,401,2),(503,404,1),(503,405,1),(504,403,1),(504,406,1),(505,407,1),(506,401,1),(507,402,1),(507,405,2),(508,403,4),(509,403,1),(510,403,1),(511,403,2),(512,403,1),(513,403,1),(514,406,2),(515,402,1),(516,407,1),(517,407,2),(518,402,1),(519,403,1),(520,404,2),(521,403,1),(522,403,2),(592,409,6),(8041,403,3),(8042,403,2),(8043,403,1),(8044,410,1),(8045,403,1);
/*!40000 ALTER TABLE `bill_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer` (
  `Customer_ID` int NOT NULL,
  `Name` varchar(50) NOT NULL,
  `Phone_No` varchar(15) DEFAULT NULL,
  `Email_ID` varchar(50) DEFAULT NULL,
  `City` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`Customer_ID`),
  UNIQUE KEY `Email_ID` (`Email_ID`),
  KEY `idx_customer_phone` (`Phone_No`),
  KEY `idx_customer_city` (`City`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
INSERT INTO `customer` VALUES (301,'Rahul Mehta','9998887777','rahul@gmail.com','Delhi'),(302,'Priya Singh','8887776666','priya@gmail.com','Noida'),(303,'Aman Verma','7776665555','aman@gmail.com','Gurgaon'),(304,'Sneha Kapoor','6665554444','sneha@gmail.com','Delhi'),(305,'Vikram Singh','5554443333','vikram@gmail.com','Faridabad'),(306,'Nisha Jain','4443332222','nisha@gmail.com','Noida'),(307,'Santosh Sharma ','1241515123','123@gmail.com','New Delhi'),(310,'Arjun Khanna','9990001111',NULL,'Delhi'),(320,'Ravi','9991112222','[ravi@gmail.com](mailto:ravi@gmail.com)','Delhi'),(906,'Sneha Roy','9876500001',NULL,'Mumbai'),(973,'Sneha Roy','9876500001',NULL,'Mumbai');
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employee`
--

DROP TABLE IF EXISTS `employee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee` (
  `Employee_ID` int NOT NULL,
  `SSN` varchar(20) NOT NULL,
  `Employee_Name` varchar(50) NOT NULL,
  `Designation` varchar(30) DEFAULT NULL,
  `Salary` decimal(10,2) DEFAULT NULL,
  `Phone_No` varchar(15) DEFAULT NULL,
  `Shop_ID` int NOT NULL,
  PRIMARY KEY (`Employee_ID`),
  UNIQUE KEY `SSN` (`SSN`),
  KEY `idx_employee_shop` (`Shop_ID`),
  KEY `idx_employee_ssn` (`SSN`),
  CONSTRAINT `employee_ibfk_1` FOREIGN KEY (`Shop_ID`) REFERENCES `shop` (`Shop_ID`) ON DELETE CASCADE,
  CONSTRAINT `employee_chk_1` CHECK ((`Salary` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employee`
--

LOCK TABLES `employee` WRITE;
/*!40000 ALTER TABLE `employee` DISABLE KEYS */;
INSERT INTO `employee` VALUES (201,'SSN001','Amit Sharma','Manager',63000.00,'9876543210',101),(202,'SSN002','Neha Verma','Cashier',58000.00,'9123456789',102),(203,'SSN003','Rohit Gupta','Sales Executive',68000.00,'9012345678',103),(204,'SSN004','Anjali Mehra','Billing Staff',75000.00,'9898989898',104),(205,'SSN005','Karan Malhotra','Store Manager',50000.00,'9090909090',103),(206,'SSN006','Pooja Nair','Cashier',24000.00,'9000011111',105),(207,'132124','Divyansh','Cashier',75000.00,'9812432224',102);
/*!40000 ALTER TABLE `employee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employee_customer`
--

DROP TABLE IF EXISTS `employee_customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee_customer` (
  `Employee_ID` int NOT NULL,
  `Customer_ID` int NOT NULL,
  `Interaction_Date` date NOT NULL,
  PRIMARY KEY (`Employee_ID`,`Customer_ID`,`Interaction_Date`),
  KEY `idx_emp_cust_employee` (`Employee_ID`),
  KEY `idx_emp_cust_customer` (`Customer_ID`),
  CONSTRAINT `employee_customer_ibfk_1` FOREIGN KEY (`Employee_ID`) REFERENCES `employee` (`Employee_ID`) ON DELETE CASCADE,
  CONSTRAINT `employee_customer_ibfk_2` FOREIGN KEY (`Customer_ID`) REFERENCES `customer` (`Customer_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employee_customer`
--

LOCK TABLES `employee_customer` WRITE;
/*!40000 ALTER TABLE `employee_customer` DISABLE KEYS */;
INSERT INTO `employee_customer` VALUES (201,301,'2025-01-21'),(201,301,'2026-03-19'),(201,301,'2026-04-08'),(201,301,'2026-04-09'),(201,305,'2026-03-19'),(201,306,'2025-01-23'),(202,302,'2025-01-20'),(202,302,'2026-03-19'),(202,302,'2026-04-09'),(202,303,'2026-03-19'),(202,303,'2026-04-08'),(202,304,'2026-03-19'),(202,305,'2026-03-19'),(203,303,'2026-03-19'),(203,304,'2025-01-22'),(203,304,'2026-03-19'),(203,305,'2026-04-18'),(204,302,'2026-03-19'),(204,303,'2025-01-21'),(205,303,'2026-03-19'),(205,303,'2026-04-18'),(205,304,'2026-03-19'),(205,304,'2026-04-18'),(205,305,'2025-01-22'),(205,305,'2026-03-19'),(205,305,'2026-04-18'),(205,307,'2026-03-19'),(206,303,'2026-03-19'),(206,306,'2025-01-22'),(206,307,'2026-03-19');
/*!40000 ALTER TABLE `employee_customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item`
--

DROP TABLE IF EXISTS `item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item` (
  `Item_ID` int NOT NULL,
  `Item_Name` varchar(50) NOT NULL,
  `Category` varchar(30) DEFAULT NULL,
  `Price` decimal(10,2) DEFAULT NULL,
  `Shop_ID` int NOT NULL,
  PRIMARY KEY (`Item_ID`),
  KEY `idx_item_shop` (`Shop_ID`),
  CONSTRAINT `item_ibfk_1` FOREIGN KEY (`Shop_ID`) REFERENCES `shop` (`Shop_ID`),
  CONSTRAINT `item_chk_1` CHECK ((`Price` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item`
--

LOCK TABLES `item` WRITE;
/*!40000 ALTER TABLE `item` DISABLE KEYS */;
INSERT INTO `item` VALUES (401,'T-Shirt','Clothing',799.00,101),(402,'Laptop','Electronics',55000.00,102),(403,'Jeans','Clothing',1999.00,103),(404,'Smartphone','Electronics',30000.00,104),(405,'Headphones','Electronics',2500.00,102),(406,'Jacket','Clothing',3499.00,101),(407,'Meal Combo','Food',499.00,105),(408,'Indian Cricket Jersey','Clothes',1500.00,101),(409,'Samsung Galaxy Notepad','Electronics',25000.00,102),(410,'Skirt','Clothes',2500.00,103),(411,'Pants','Clothing ',1000.00,103);
/*!40000 ALTER TABLE `item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mall`
--

DROP TABLE IF EXISTS `mall`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mall` (
  `Mall_ID` int NOT NULL,
  `Mall_Name` varchar(50) NOT NULL,
  `Location` varchar(50) DEFAULT NULL,
  `Total_Floors` int DEFAULT NULL,
  PRIMARY KEY (`Mall_ID`),
  CONSTRAINT `mall_chk_1` CHECK ((`Total_Floors` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mall`
--

LOCK TABLES `mall` WRITE;
/*!40000 ALTER TABLE `mall` DISABLE KEYS */;
INSERT INTO `mall` VALUES (1,'City Center Mall','Delhi',5),(2,'Grand Plaza Mall','Noida',4);
/*!40000 ALTER TABLE `mall` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parking_record`
--

DROP TABLE IF EXISTS `parking_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parking_record` (
  `Parking_ID` int NOT NULL,
  `Vehicle_Number` varchar(20) DEFAULT NULL,
  `Entry_Time` datetime DEFAULT NULL,
  `Exit_Time` datetime DEFAULT NULL,
  `Duration` int DEFAULT NULL,
  `Parking_Fee` decimal(10,2) DEFAULT NULL,
  `Slot_ID` int NOT NULL,
  PRIMARY KEY (`Parking_ID`),
  KEY `idx_parking_vehicle` (`Vehicle_Number`),
  KEY `idx_parking_slot` (`Slot_ID`),
  CONSTRAINT `parking_record_ibfk_1` FOREIGN KEY (`Slot_ID`) REFERENCES `parking_slot` (`Slot_ID`),
  CONSTRAINT `parking_record_chk_1` CHECK ((`Duration` >= 0)),
  CONSTRAINT `parking_record_chk_2` CHECK ((`Parking_Fee` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parking_record`
--

LOCK TABLES `parking_record` WRITE;
/*!40000 ALTER TABLE `parking_record` DISABLE KEYS */;
INSERT INTO `parking_record` VALUES (701,'DL8CAF1234','2025-01-20 17:45:00','2025-01-20 19:45:00',120,100.00,601),(702,'HR26AB4567','2025-01-21 15:00:00','2025-01-21 17:30:00',150,120.00,602),(703,'DL3CB7890','2025-01-21 18:10:00','2025-01-21 19:00:00',50,40.00,603),(704,'UP14XY1111','2025-01-22 12:30:00','2025-01-22 14:00:00',90,80.00,604),(705,'DL9ZZ9999','2025-01-22 19:00:00','2025-01-22 21:00:00',120,100.00,601),(706,'HR10MN4321','2025-01-23 16:20:00','2025-01-23 17:20:00',60,50.00,605),(707,'A11','2026-03-19 11:06:58','2026-03-19 11:07:23',1,0.83,603),(708,'A55','2026-03-19 12:00:42','2026-03-19 12:02:15',1,0.83,601),(709,'DL53324532','2026-03-19 13:27:47','2026-04-08 19:33:56',29166,24305.00,604),(710,'DL432252234','2026-04-08 19:33:18','2026-04-08 19:33:43',1,0.83,601),(711,'2345','2026-04-18 20:02:05',NULL,NULL,NULL,601),(712,'23457','2026-04-18 20:05:29',NULL,NULL,NULL,603),(713,'456','2026-04-18 20:14:48',NULL,NULL,NULL,604);
/*!40000 ALTER TABLE `parking_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parking_slot`
--

DROP TABLE IF EXISTS `parking_slot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parking_slot` (
  `Slot_ID` int NOT NULL,
  `Slot_Number` varchar(10) DEFAULT NULL,
  `Slot_Type` varchar(20) DEFAULT NULL,
  `Floor_No` int DEFAULT NULL,
  `Mall_ID` int NOT NULL,
  PRIMARY KEY (`Slot_ID`),
  KEY `Mall_ID` (`Mall_ID`),
  CONSTRAINT `parking_slot_ibfk_1` FOREIGN KEY (`Mall_ID`) REFERENCES `mall` (`Mall_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parking_slot`
--

LOCK TABLES `parking_slot` WRITE;
/*!40000 ALTER TABLE `parking_slot` DISABLE KEYS */;
INSERT INTO `parking_slot` VALUES (601,'A1','Car',0,1),(602,'A2','Car',0,1),(603,'B1','Bike',-1,1),(604,'B2','Bike',-1,1),(605,'C1','Car',0,2),(606,'A11','Car',1,2),(607,'A7','Truck',1,1),(608,'A22','Car',1,1),(610,'D1','Car',1,1);
/*!40000 ALTER TABLE `parking_slot` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shop`
--

DROP TABLE IF EXISTS `shop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shop` (
  `Shop_ID` int NOT NULL,
  `Shop_Name` varchar(50) NOT NULL,
  `Category` varchar(30) DEFAULT NULL,
  `Owner_Name` varchar(50) DEFAULT NULL,
  `Floor_No` int DEFAULT NULL,
  `Mall_ID` int NOT NULL,
  PRIMARY KEY (`Shop_ID`),
  KEY `idx_shop_floor` (`Floor_No`),
  KEY `idx_shop_mall` (`Mall_ID`),
  CONSTRAINT `shop_ibfk_1` FOREIGN KEY (`Mall_ID`) REFERENCES `mall` (`Mall_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shop`
--

LOCK TABLES `shop` WRITE;
/*!40000 ALTER TABLE `shop` DISABLE KEYS */;
INSERT INTO `shop` VALUES (101,'Trends','Clothing','Transaction B wants 101',1,1),(102,'Croma','Electronics','Transaction A wants 102',2,1),(103,'Pantaloons','Clothing','Aditya Birla',3,1),(104,'Reliance Digital','Electronics','Reliance',4,1),(105,'Food Court','Restaurant','Mall Ops',2,2);
/*!40000 ALTER TABLE `shop` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `bill_details`
--

/*!50001 DROP VIEW IF EXISTS `bill_details`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `bill_details` AS select `b`.`Bill_ID` AS `Bill_ID`,`c`.`Name` AS `Customer_Name`,`s`.`Shop_Name` AS `Shop_Name`,`b`.`Final_Amount` AS `Final_Amount` from ((`bill` `b` join `customer` `c` on((`b`.`Customer_ID` = `c`.`Customer_ID`))) join `shop` `s` on((`b`.`Shop_ID` = `s`.`Shop_ID`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-10 23:25:45
