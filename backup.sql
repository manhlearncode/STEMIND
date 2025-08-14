-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: localhost    Database: stemind_db
-- ------------------------------------------------------
-- Server version	8.0.42-0ubuntu0.22.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Chatbot_chatmessage`
--

DROP TABLE IF EXISTS `Chatbot_chatmessage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Chatbot_chatmessage` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `message_type` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  `session_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Chatbot_chatmessage_session_id_ed73036a_fk_Chatbot_c` (`session_id`),
  CONSTRAINT `Chatbot_chatmessage_session_id_ed73036a_fk_Chatbot_c` FOREIGN KEY (`session_id`) REFERENCES `Chatbot_chatsession` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Chatbot_chatmessage`
--

LOCK TABLES `Chatbot_chatmessage` WRITE;
/*!40000 ALTER TABLE `Chatbot_chatmessage` DISABLE KEYS */;
INSERT INTO `Chatbot_chatmessage` VALUES (1,'user','Tôi muốn tạo bài giảng cho môn khoa học của lớp 5.','2025-08-12 11:01:07.484292',1),(2,'bot','Chào bạn, tôi rất vui được hỗ trợ bạn tạo bài giảng khoa học cho lớp 5 theo hướng STEM. Dựa trên tài liệu bạn cung cấp và kiến thức của tôi, đây là một số gợi ý và hướng dẫn chi tiết:\n\n**1. Xác định Chủ Đề:**\n\n*   **Mạch điện đơn giản (đề xuất từ bài đăng của admin):** Chủ đề này rất phù hợp với học sinh lớp 5, vừa trực quan, vừa dễ thực hiện các hoạt động thực hành.\n*   **Các chủ đề khác (dựa trên kiến thức của tôi):**\n    *   **Ánh sáng và bóng tối:** Thí nghiệm về sự truyền thẳng của ánh sáng, tạo bóng, các loại vật liệu (trong suốt, mờ đục,...)\n    *   **Âm thanh:** Nguồn âm thanh, sự lan truyền âm thanh, các yếu tố ảnh hưởng đến âm thanh (độ cao, độ to).\n    *   **Thực vật:** Các bộ phận của cây và chức năng của chúng, quá trình quang hợp (giới thiệu đơn giản), vòng đời của cây.\n    *   **Động vật:** Phân loại động vật (ví dụ: có xương sống/không xương sống), môi trường sống của động vật, chuỗi thức ăn.\n    *   **Thời tiết:** Các yếu tố của thời tiết (nhiệt độ, gió, mưa), các loại mây, dự báo thời tiết (giới thiệu cơ bản).\n\n**2. Tìm hiểu Tài Liệu:**\n\n*   **\"Tài liệu giáo dục STEM tiểu học\":** Đây là tài liệu quan trọng nhất. Hãy đọc kỹ để hiểu:\n    *   **Phương pháp tích hợp giáo dục STEM:** Tìm hiểu cách kết hợp Khoa học, Công nghệ, Kỹ thuật và Toán học vào bài giảng.\n    *   **Chủ đề và hoạt động thực hành:** Xem xét các chủ đề và hoạt động đã được đề xuất trong tài liệu. Có thể có những gợi ý phù hợp với chủ đề bạn đã chọn.\n    *   **Dự án trải nghiệm:** Tìm kiếm các dự án trải nghiệm liên quan đến chủ đề của bạn. Các dự án này giúp học sinh phát triển tư duy logic, khả năng giải quyết vấn đề và sáng tạo.\n    *   **Cách xây dựng bài giảng liên môn:** Tìm hiểu cách kết nối chủ đề khoa học với các môn học khác (ví dụ: Toán học, Công nghệ, Nghệ thuật).\n*   **\"Tài liệu tập huấn về giáo dục STEM\":** Tài liệu này cung cấp kiến thức nền tảng và phương pháp triển khai giáo dục STEM. Hãy đọc để hiểu:\n    *   **Cơ sở lý luận về STEM:** Hiểu rõ hơn về triết lý và mục tiêu của giáo dục STEM.\n    *   **Hướng dẫn thiết kế bài học STEM:** Tìm hiểu các bước thiết kế một bài học STEM hiệu quả.\n    *   **Xây dựng chủ đề liên môn:** Tìm hiểu cách xây dựng các chủ đề liên môn hấp dẫn và phù hợp với học sinh lớp 5.\n    *   **Tổ chức hoạt động trải nghiệm:** Tìm hiểu cách tổ chức các hoạt động trải nghiệm thú vị và bổ ích cho học sinh.\n    *   **Đánh giá kết quả học tập:** Tìm hiểu cách đánh giá kết quả học tập của học sinh theo hướng STEM.\n\n**3. Xây Dựng Bài Giảng (Ví dụ: Mạch Điện Đơn Giản):**\n\n*   **Mục tiêu:**\n    *   Học sinh nhận biết các thành phần của một mạch điện đơn giản (nguồn điện, dây dẫn, công tắc, thiết bị tiêu thụ điện).\n    *   Học sinh hiểu vai trò của từng thành phần trong mạch điện.\n    *   Học sinh lắp ráp được một mạch điện đơn giản.\n    *   Học sinh giải thích được nguyên lý hoạt động của mạch điện.\n    *   Học sinh thực hành an toàn khi sử dụng điện.\n*   **Nội dung:**\n    *   Giới thiệu về điện và tầm quan trọng của điện trong cuộc sống.\n    *   Các thành phần của mạch điện:\n        *   Nguồn điện: Pin, ắc quy.\n        *   Dây dẫn: Dây điện.\n        *   Công tắc: Bật/tắt dòng điện.\n        *   Thiết bị tiêu thụ điện: Bóng đèn.\n    *   Mạch điện kín và mạch điện hở.\n    *   Nguyên lý hoạt động của mạch điện.\n    *   An toàn khi sử dụng điện.\n*   **Hoạt động:**\n    *   **Khởi động (5 phút):**\n        *   Đặt câu hỏi: \"Các em sử dụng những đồ dùng nào cần điện?\"\n        *   Thảo luận về tầm quan trọng của điện.\n    *   **Khám phá (15 phút):**\n        *   Giới thiệu các thành phần của mạch điện (pin, dây dẫn, công tắc, bóng đèn).\n        *   Cho học sinh quan sát và sờ vào các thành phần (lưu ý an toàn).\n        *   Yêu cầu học sinh dự đoán điều gì sẽ xảy ra khi kết nối các thành phần lại với nhau.\n    *   **Thực hành (20 phút):**\n        *   Chia học sinh thành các nhóm nhỏ.\n        *   Phát cho mỗi nhóm một bộ dụng cụ để lắp mạch điện đơn giản.\n        *   Hướng dẫn học sinh lắp mạch điện theo từng bước.\n        *   Quan sát và hỗ trợ học sinh trong quá trình thực hành.\n    *   **Giải thích (10 phút):**\n        *   Yêu cầu học sinh giải thích tại sao bóng đèn sáng khi mạch điện kín và không sáng khi mạch điện hở.\n        *   Giải thích nguyên lý hoạt động của mạch điện.\n    *   **Mở rộng (5 phút):**\n        *   Gợi ý học sinh tìm hiểu về các loại mạch điện khác (ví dụ: mạch điện nối tiếp, mạch điện song song).\n        *   Thảo luận về cách tiết kiệm điện.\n*   **Đánh giá:**\n    *   Quan sát học sinh trong quá trình thực hành.\n    *   Yêu cầu học sinh giải thích nguyên lý hoạt động của mạch điện.\n    *   Cho học sinh làm bài tập trắc nghiệm hoặc bài tập thực hành.\n*   **Liên môn:**\n    *   **Toán học:** Sử dụng các phép đo để tính toán chiều dài dây dẫn.\n    *   **Công nghệ:** Tìm hiểu về các loại vật liệu dẫn điện và cách điện.\n    *   **Nghệ thuật:** Thiết kế một chiếc đèn đơn giản sử dụng mạch điện.\n\n**4. Lưu Ý Quan Trọng:**\n\n*   **An toàn:** Luôn đặt sự an toàn lên hàng đầu khi thực hiện các thí nghiệm liên quan đến điện. Sử dụng pin có điện áp thấp (dưới 6V) và giám sát chặt chẽ học sinh.\n*   **Trực quan:** Sử dụng hình ảnh, video, và các vật dụng trực quan để minh họa các khái niệm khoa học.\n*   **Tương tác:** Khuyến khích học sinh đặt câu hỏi, tham gia thảo luận, và chia sẻ ý tưởng.\n*   **Thực tế:** Liên hệ các kiến thức khoa học với thực tế cuộc sống để giúp học sinh hiểu rõ hơn về ứng dụng của khoa học.\n*   **Điều chỉnh:** Điều chỉnh bài giảng cho phù hợp với trình độ và khả năng của học sinh.\n\n**Lời khuyên:**\n\n*   Hãy bắt đầu với những thí nghiệm đơn giản và dễ thực hiện.\n*   Tạo ra một môi trường học tập vui vẻ và khuyến khích sự sáng tạo.\n*   Tìm kiếm thêm tài liệu và ý tưởng trên internet.\n\nChúc bạn thành công trong việc tạo bài giảng khoa học STEM cho lớp 5! Nếu bạn có bất kỳ câu hỏi nào khác, đừng ngần ngại hỏi tôi.\n','2025-08-12 11:01:21.380800',1);
/*!40000 ALTER TABLE `Chatbot_chatmessage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Chatbot_chatsession`
--

DROP TABLE IF EXISTS `Chatbot_chatsession`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Chatbot_chatsession` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `session_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_id` (`session_id`),
  KEY `Chatbot_chatsession_user_id_3d003617_fk_auth_user_id` (`user_id`),
  CONSTRAINT `Chatbot_chatsession_user_id_3d003617_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Chatbot_chatsession`
--

LOCK TABLES `Chatbot_chatsession` WRITE;
/*!40000 ALTER TABLE `Chatbot_chatsession` DISABLE KEYS */;
INSERT INTO `Chatbot_chatsession` VALUES (1,'chat_1754358236209_ubszckiv4','Chat with Files','2025-08-12 11:01:07.473450','2025-08-12 11:01:07.473491',NULL);
/*!40000 ALTER TABLE `Chatbot_chatsession` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Chatbot_fileattachment`
--

DROP TABLE IF EXISTS `Chatbot_fileattachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Chatbot_fileattachment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `original_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_size` int unsigned NOT NULL,
  `mime_type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `uploaded_at` datetime(6) NOT NULL,
  `message_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Chatbot_fileattachme_message_id_627beb66_fk_Chatbot_c` (`message_id`),
  CONSTRAINT `Chatbot_fileattachme_message_id_627beb66_fk_Chatbot_c` FOREIGN KEY (`message_id`) REFERENCES `Chatbot_chatmessage` (`id`),
  CONSTRAINT `Chatbot_fileattachment_chk_1` CHECK ((`file_size` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Chatbot_fileattachment`
--

LOCK TABLES `Chatbot_fileattachment` WRITE;
/*!40000 ALTER TABLE `Chatbot_fileattachment` DISABLE KEYS */;
/*!40000 ALTER TABLE `Chatbot_fileattachment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `File_sharing_platform_category`
--

DROP TABLE IF EXISTS `File_sharing_platform_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `File_sharing_platform_category` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `parent_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `File_sharing_platform_category_name_parent_id_a20febc3_uniq` (`name`,`parent_id`),
  KEY `File_sharing_platfor_parent_id_76811c06_fk_File_shar` (`parent_id`),
  CONSTRAINT `File_sharing_platfor_parent_id_76811c06_fk_File_shar` FOREIGN KEY (`parent_id`) REFERENCES `File_sharing_platform_category` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `File_sharing_platform_category`
--

LOCK TABLES `File_sharing_platform_category` WRITE;
/*!40000 ALTER TABLE `File_sharing_platform_category` DISABLE KEYS */;
INSERT INTO `File_sharing_platform_category` VALUES (1,'Theo đối tượng',NULL,'2025-08-12 11:01:48.873752','2025-08-12 11:01:48.873787',NULL),(2,'Theo lĩnh vực',NULL,'2025-08-12 11:02:11.331318','2025-08-12 11:02:11.331353',NULL),(3,'Theo thể loại',NULL,'2025-08-12 11:02:23.773381','2025-08-12 11:02:23.773419',NULL),(4,'Theo khu vực',NULL,'2025-08-12 11:02:34.113326','2025-08-12 11:02:34.113363',NULL),(5,'Lớp 1',NULL,'2025-08-12 11:02:55.951341','2025-08-12 11:02:55.951381',1),(6,'Lớp 2',NULL,'2025-08-12 11:03:18.968189','2025-08-12 11:03:18.968227',1),(7,'Lớp 3',NULL,'2025-08-12 11:03:30.553453','2025-08-12 11:03:30.553491',1),(8,'Lớp 4',NULL,'2025-08-12 11:03:44.935563','2025-08-12 11:03:44.935603',1),(9,'Lớp 5',NULL,'2025-08-12 11:04:12.285429','2025-08-12 11:04:12.285468',1),(10,'Khoa học',NULL,'2025-08-12 11:04:54.913249','2025-08-12 11:04:54.913302',2),(11,'Toán học',NULL,'2025-08-12 11:05:27.933874','2025-08-12 11:05:27.933912',2),(12,'Tự nhiên - Xã hội',NULL,'2025-08-12 11:05:44.167816','2025-08-12 11:05:44.167856',2),(13,'Địa lý - Lịch sử',NULL,'2025-08-12 11:05:58.634383','2025-08-12 11:05:58.634421',2),(14,'Công nghệ',NULL,'2025-08-12 11:06:18.384525','2025-08-12 11:06:18.384566',2),(15,'Nghệ thuật',NULL,'2025-08-12 11:06:38.590382','2025-08-12 11:06:38.590421',2),(16,'Bài giảng',NULL,'2025-08-12 11:07:03.748719','2025-08-12 11:07:03.748759',3),(17,'Giáo trình',NULL,'2025-08-12 11:07:20.211297','2025-08-12 11:07:20.211337',3),(18,'Bài tập',NULL,'2025-08-12 11:07:34.185237','2025-08-12 11:07:34.185294',3),(19,'Bài kiểm tra',NULL,'2025-08-12 11:07:50.563015','2025-08-12 11:07:50.563053',3),(20,'Thể loại khác',NULL,'2025-08-12 11:08:11.100973','2025-08-12 11:08:11.101012',3),(21,'Hà Nội',NULL,'2025-08-12 11:08:26.240945','2025-08-12 11:08:26.240984',4),(22,'Hà Tĩnh',NULL,'2025-08-12 11:08:39.810947','2025-08-12 11:08:39.810985',4),(23,'Nghệ An',NULL,'2025-08-12 11:08:51.677806','2025-08-12 11:08:51.677843',4),(24,'Khu vực khác',NULL,'2025-08-12 11:09:27.490129','2025-08-12 11:09:27.490136',4);
/*!40000 ALTER TABLE `File_sharing_platform_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `File_sharing_platform_favorite`
--

DROP TABLE IF EXISTS `File_sharing_platform_favorite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `File_sharing_platform_favorite` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  `file_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `File_sharing_platform_favorite_user_id_file_id_30b58383_uniq` (`user_id`,`file_id`),
  KEY `File_sharing_platfor_file_id_5258026b_fk_File_shar` (`file_id`),
  CONSTRAINT `File_sharing_platfor_file_id_5258026b_fk_File_shar` FOREIGN KEY (`file_id`) REFERENCES `File_sharing_platform_file` (`id`),
  CONSTRAINT `File_sharing_platform_favorite_user_id_d8b84776_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `File_sharing_platform_favorite`
--

LOCK TABLES `File_sharing_platform_favorite` WRITE;
/*!40000 ALTER TABLE `File_sharing_platform_favorite` DISABLE KEYS */;
/*!40000 ALTER TABLE `File_sharing_platform_favorite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `File_sharing_platform_file`
--

DROP TABLE IF EXISTS `File_sharing_platform_file`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `File_sharing_platform_file` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_thumbnail` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `file_description` longtext COLLATE utf8mb4_unicode_ci,
  `file_urls` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_status` int NOT NULL,
  `file_price` int unsigned NOT NULL,
  `file_downloads` int unsigned NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `author_id` bigint NOT NULL,
  `extension_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`),
  KEY `File_sharing_platform_file_author_id_af4feed2_fk_auth_user_id` (`author_id`),
  KEY `File_sharing_platfor_extension_id_d3110b84_fk_File_shar` (`extension_id`),
  CONSTRAINT `File_sharing_platfor_extension_id_d3110b84_fk_File_shar` FOREIGN KEY (`extension_id`) REFERENCES `File_sharing_platform_fileextension` (`id`),
  CONSTRAINT `File_sharing_platform_file_author_id_af4feed2_fk_auth_user_id` FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `File_sharing_platform_file_chk_1` CHECK ((`file_price` >= 0)),
  CONSTRAINT `File_sharing_platform_file_chk_2` CHECK ((`file_downloads` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `File_sharing_platform_file`
--

LOCK TABLES `File_sharing_platform_file` WRITE;
/*!40000 ALTER TABLE `File_sharing_platform_file` DISABLE KEYS */;
INSERT INTO `File_sharing_platform_file` VALUES (2,'Giới thiệu về nền tảng STEMIND','thumbnails/25/08/14/Logo.png','STEMIND là nền tảng trực tuyến tích hợp AI được thiết kế để giúp giáo viên nhanh chóng thiết kế bài giảng STEM, tìm kiếm tài liệu học tập phù hợp và tổ chức các hoạt động. Với giao diện thân thiện, tiết kiệm thời gian, nâng cao chất lượng giảng dạy và kết nối cộng đồng.','uploads/25/08/13/STEMIND_.mov',0,0,0,'2025-08-14 02:34:13.563106','2025-08-14 02:51:30.285205',1,1),(3,'Chuyên đề các vùng kinh tế','','Giới thiệu đặc điểm, tiềm năng, thế mạnh và định hướng phát triển của các vùng kinh tế, giúp hiểu vai trò và mối liên kết giữa các vùng trong nền kinh tế.','uploads/25/08/14/CHUYÊN_ĐỀ_CÁC_VÙNG_KINH_TẾ_uDbc2sp.docx',0,0,0,'2025-08-14 03:00:06.603703','2025-08-14 03:00:06.603749',1,1);
/*!40000 ALTER TABLE `File_sharing_platform_file` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `File_sharing_platform_file_categories`
--

DROP TABLE IF EXISTS `File_sharing_platform_file_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `File_sharing_platform_file_categories` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file_id` bigint NOT NULL,
  `category_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `File_sharing_platform_fi_file_id_category_id_9d790d85_uniq` (`file_id`,`category_id`),
  KEY `File_sharing_platfor_category_id_75d3ccd1_fk_File_shar` (`category_id`),
  CONSTRAINT `File_sharing_platfor_category_id_75d3ccd1_fk_File_shar` FOREIGN KEY (`category_id`) REFERENCES `File_sharing_platform_category` (`id`),
  CONSTRAINT `File_sharing_platfor_file_id_0caac958_fk_File_shar` FOREIGN KEY (`file_id`) REFERENCES `File_sharing_platform_file` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `File_sharing_platform_file_categories`
--

LOCK TABLES `File_sharing_platform_file_categories` WRITE;
/*!40000 ALTER TABLE `File_sharing_platform_file_categories` DISABLE KEYS */;
INSERT INTO `File_sharing_platform_file_categories` VALUES (19,2,1),(20,2,2),(21,2,3),(22,2,4),(23,2,5),(24,2,6),(25,2,7),(26,2,8),(9,2,9),(10,2,10),(27,2,11),(11,2,12),(12,2,13),(28,2,14),(29,2,15),(13,2,16),(14,2,17),(30,2,18),(31,2,19),(32,2,20),(15,2,21),(16,2,22),(17,2,23),(18,2,24),(33,3,9),(34,3,10),(35,3,12),(36,3,13),(37,3,16),(38,3,17),(39,3,21),(40,3,22),(41,3,23),(42,3,24);
/*!40000 ALTER TABLE `File_sharing_platform_file_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `File_sharing_platform_fileextension`
--

DROP TABLE IF EXISTS `File_sharing_platform_fileextension`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `File_sharing_platform_fileextension` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `extension_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `File_sharing_platform_fileextension`
--

LOCK TABLES `File_sharing_platform_fileextension` WRITE;
/*!40000 ALTER TABLE `File_sharing_platform_fileextension` DISABLE KEYS */;
INSERT INTO `File_sharing_platform_fileextension` VALUES (1,'document','2025-08-12 11:10:31.684974','2025-08-12 11:10:31.685017');
/*!40000 ALTER TABLE `File_sharing_platform_fileextension` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Social_Platform_comment`
--

DROP TABLE IF EXISTS `Social_Platform_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Social_Platform_comment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `content` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `post_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Social_Platform_comm_post_id_be71ecf7_fk_Social_Pl` (`post_id`),
  KEY `Social_Platform_comment_user_id_3f44170d_fk_auth_user_id` (`user_id`),
  CONSTRAINT `Social_Platform_comm_post_id_be71ecf7_fk_Social_Pl` FOREIGN KEY (`post_id`) REFERENCES `Social_Platform_post` (`id`),
  CONSTRAINT `Social_Platform_comment_user_id_3f44170d_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Social_Platform_comment`
--

LOCK TABLES `Social_Platform_comment` WRITE;
/*!40000 ALTER TABLE `Social_Platform_comment` DISABLE KEYS */;
/*!40000 ALTER TABLE `Social_Platform_comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Social_Platform_like`
--

DROP TABLE IF EXISTS `Social_Platform_like`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Social_Platform_like` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `post_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `Social_Platform_like_user_id_post_id_262b7be5_uniq` (`user_id`,`post_id`),
  KEY `Social_Platform_like_post_id_6cd0307a_fk_Social_Platform_post_id` (`post_id`),
  CONSTRAINT `Social_Platform_like_post_id_6cd0307a_fk_Social_Platform_post_id` FOREIGN KEY (`post_id`) REFERENCES `Social_Platform_post` (`id`),
  CONSTRAINT `Social_Platform_like_user_id_759cbc97_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Social_Platform_like`
--

LOCK TABLES `Social_Platform_like` WRITE;
/*!40000 ALTER TABLE `Social_Platform_like` DISABLE KEYS */;
/*!40000 ALTER TABLE `Social_Platform_like` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Social_Platform_pointsettings`
--

DROP TABLE IF EXISTS `Social_Platform_pointsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Social_Platform_pointsettings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `upload_file_points` int NOT NULL,
  `create_post_points` int NOT NULL,
  `like_post_points` int NOT NULL,
  `share_post_points` int NOT NULL,
  `comment_points` int NOT NULL,
  `view_free_file_cost` int NOT NULL,
  `download_free_file_cost` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Social_Platform_pointsettings`
--

LOCK TABLES `Social_Platform_pointsettings` WRITE;
/*!40000 ALTER TABLE `Social_Platform_pointsettings` DISABLE KEYS */;
INSERT INTO `Social_Platform_pointsettings` VALUES (1,10,1,1,1,1,1,5);
/*!40000 ALTER TABLE `Social_Platform_pointsettings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Social_Platform_pointtransaction`
--

DROP TABLE IF EXISTS `Social_Platform_pointtransaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Social_Platform_pointtransaction` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `transaction_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `points` int NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `related_object_id` int DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Social_Platform_poin_user_id_bcfc35de_fk_auth_user` (`user_id`),
  CONSTRAINT `Social_Platform_poin_user_id_bcfc35de_fk_auth_user` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Social_Platform_pointtransaction`
--

LOCK TABLES `Social_Platform_pointtransaction` WRITE;
/*!40000 ALTER TABLE `Social_Platform_pointtransaction` DISABLE KEYS */;
INSERT INTO `Social_Platform_pointtransaction` VALUES (1,'upload_file',10,'Uploaded a file',1,'2025-08-12 11:10:32.101124',1),(2,'view_free_file',-1,'Viewed a free file',1,'2025-08-12 11:10:36.200544',1),(3,'view_free_file',-1,'Viewed a free file',1,'2025-08-13 13:53:01.735880',1),(4,'view_free_file',-1,'Viewed a free file',1,'2025-08-13 13:54:34.135727',1),(5,'view_free_file',-1,'Viewed a free file',1,'2025-08-14 02:22:10.164622',1),(6,'view_free_file',-1,'Viewed a free file',1,'2025-08-14 02:26:56.313101',1),(7,'view_free_file',-1,'Viewed a free file',1,'2025-08-14 02:31:06.960868',1),(8,'view_free_file',-1,'Viewed a free file',1,'2025-08-14 02:32:12.330955',1),(9,'upload_file',10,'Uploaded a file',2,'2025-08-14 02:34:13.598914',1),(10,'view_free_file',-1,'Viewed a free file',2,'2025-08-14 02:34:20.912966',1),(11,'view_free_file',-1,'Viewed a free file',2,'2025-08-14 02:51:42.467645',1),(12,'view_free_file',-1,'Viewed a free file',2,'2025-08-14 02:52:09.344402',1),(13,'view_free_file',-1,'Viewed a free file',2,'2025-08-14 02:53:52.823166',1),(14,'view_free_file',-1,'Viewed a free file',2,'2025-08-14 02:56:15.114933',1),(15,'upload_file',10,'Uploaded a file',3,'2025-08-14 03:00:06.639892',1),(16,'view_free_file',-1,'Viewed a free file',3,'2025-08-14 03:00:11.302240',1),(17,'view_free_file',-1,'Viewed a free file',3,'2025-08-14 03:05:57.875510',1),(18,'view_free_file',-1,'Viewed a free file',2,'2025-08-14 03:06:06.474548',1),(19,'view_free_file',-1,'Viewed a free file',3,'2025-08-14 03:06:21.052521',1),(20,'view_free_file',-1,'Viewed a free file',3,'2025-08-14 03:07:22.540693',1),(21,'view_free_file',-1,'Viewed a free file',3,'2025-08-14 03:08:35.400868',1),(22,'view_free_file',-1,'Viewed a free file',3,'2025-08-14 03:08:56.734003',1),(23,'view_free_file',-1,'Viewed a free file',3,'2025-08-14 03:10:52.346148',1),(24,'view_free_file',-1,'Viewed a free file',2,'2025-08-14 03:11:02.000774',1),(25,'view_free_file',-1,'Viewed a free file',3,'2025-08-14 06:04:18.379163',1);
/*!40000 ALTER TABLE `Social_Platform_pointtransaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Social_Platform_post`
--

DROP TABLE IF EXISTS `Social_Platform_post`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Social_Platform_post` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `content` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `image` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `author_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Social_Platform_post_author_id_da753837_fk_auth_user_id` (`author_id`),
  CONSTRAINT `Social_Platform_post_author_id_da753837_fk_auth_user_id` FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Social_Platform_post`
--

LOCK TABLES `Social_Platform_post` WRITE;
/*!40000 ALTER TABLE `Social_Platform_post` DISABLE KEYS */;
/*!40000 ALTER TABLE `Social_Platform_post` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Social_Platform_userprofile`
--

DROP TABLE IF EXISTS `Social_Platform_userprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Social_Platform_userprofile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bio` longtext COLLATE utf8mb4_unicode_ci,
  `avatar` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `points` int NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `Social_Platform_userprofile_user_id_3bcf6a0f_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Social_Platform_userprofile`
--

LOCK TABLES `Social_Platform_userprofile` WRITE;
/*!40000 ALTER TABLE `Social_Platform_userprofile` DISABLE KEYS */;
INSERT INTO `Social_Platform_userprofile` VALUES (1,NULL,'',8,1),(3,'','',0,3),(4,'','',0,4),(5,NULL,'',0,5),(6,'','',0,6);
/*!40000 ALTER TABLE `Social_Platform_userprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Social_Platform_userprofile_followers`
--

DROP TABLE IF EXISTS `Social_Platform_userprofile_followers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Social_Platform_userprofile_followers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `userprofile_id` bigint NOT NULL,
  `customuser_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `Social_Platform_userprof_userprofile_id_customuse_4c3cd5dd_uniq` (`userprofile_id`,`customuser_id`),
  KEY `Social_Platform_user_customuser_id_1e438ec2_fk_auth_user` (`customuser_id`),
  CONSTRAINT `Social_Platform_user_customuser_id_1e438ec2_fk_auth_user` FOREIGN KEY (`customuser_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `Social_Platform_user_userprofile_id_d2ba673e_fk_Social_Pl` FOREIGN KEY (`userprofile_id`) REFERENCES `Social_Platform_userprofile` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Social_Platform_userprofile_followers`
--

LOCK TABLES `Social_Platform_userprofile_followers` WRITE;
/*!40000 ALTER TABLE `Social_Platform_userprofile_followers` DISABLE KEYS */;
/*!40000 ALTER TABLE `Social_Platform_userprofile_followers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=77 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add Favorite',6,'add_favorite'),(22,'Can change Favorite',6,'change_favorite'),(23,'Can delete Favorite',6,'delete_favorite'),(24,'Can view Favorite',6,'view_favorite'),(25,'Can add File',7,'add_file'),(26,'Can change File',7,'change_file'),(27,'Can delete File',7,'delete_file'),(28,'Can view File',7,'view_file'),(29,'Can add file extension',8,'add_fileextension'),(30,'Can change file extension',8,'change_fileextension'),(31,'Can delete file extension',8,'delete_fileextension'),(32,'Can view file extension',8,'view_fileextension'),(33,'Can add category',9,'add_category'),(34,'Can change category',9,'change_category'),(35,'Can delete category',9,'delete_category'),(36,'Can view category',9,'view_category'),(37,'Can add Chat Message',10,'add_chatmessage'),(38,'Can change Chat Message',10,'change_chatmessage'),(39,'Can delete Chat Message',10,'delete_chatmessage'),(40,'Can view Chat Message',10,'view_chatmessage'),(41,'Can add Chat Session',11,'add_chatsession'),(42,'Can change Chat Session',11,'change_chatsession'),(43,'Can delete Chat Session',11,'delete_chatsession'),(44,'Can view Chat Session',11,'view_chatsession'),(45,'Can add File Attachment',12,'add_fileattachment'),(46,'Can change File Attachment',12,'change_fileattachment'),(47,'Can delete File Attachment',12,'delete_fileattachment'),(48,'Can view File Attachment',12,'view_fileattachment'),(49,'Can add Point Settings',13,'add_pointsettings'),(50,'Can change Point Settings',13,'change_pointsettings'),(51,'Can delete Point Settings',13,'delete_pointsettings'),(52,'Can view Point Settings',13,'view_pointsettings'),(53,'Can add User',14,'add_customuser'),(54,'Can change User',14,'change_customuser'),(55,'Can delete User',14,'delete_customuser'),(56,'Can view User',14,'view_customuser'),(57,'Can add user profile',15,'add_userprofile'),(58,'Can change user profile',15,'change_userprofile'),(59,'Can delete user profile',15,'delete_userprofile'),(60,'Can view user profile',15,'view_userprofile'),(61,'Can add post',16,'add_post'),(62,'Can change post',16,'change_post'),(63,'Can delete post',16,'delete_post'),(64,'Can view post',16,'view_post'),(65,'Can add point transaction',17,'add_pointtransaction'),(66,'Can change point transaction',17,'change_pointtransaction'),(67,'Can delete point transaction',17,'delete_pointtransaction'),(68,'Can view point transaction',17,'view_pointtransaction'),(69,'Can add comment',18,'add_comment'),(70,'Can change comment',18,'change_comment'),(71,'Can delete comment',18,'delete_comment'),(72,'Can view comment',18,'view_comment'),(73,'Can add like',19,'add_like'),(74,'Can change like',19,'change_like'),(75,'Can delete like',19,'delete_like'),(76,'Can view like',19,'view_like');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `lastname` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `firstname` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `age` int unsigned DEFAULT NULL,
  `address` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  CONSTRAINT `auth_user_chk_1` CHECK ((`age` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1000000$wMzHTvRLQjttCYDp855dlB$qDQ+cyphveragUDlEoULsZLbmMQTYCdN1JIckXV+m1I=','2025-08-14 01:06:17.545566',1,'admin','','','admin@gmail.com',1,1,'2025-08-12 10:58:51.950285','','',NULL,'',''),(3,'pbkdf2_sha256$1000000$10Ozac1OYLAxNljHpC4ql4$BPeSP4AMowNzF/O81C6TU2poIezH4z+V4SCR/Hgc5x8=','2025-08-13 10:36:10.216441',0,'NguyenTuKien','','','KienNT.B23CN465@stu.ptit.edu.vn',0,1,'2025-08-13 10:36:09.414921','Nguyễn','Kiên',NULL,'Số 1, Ngõ 85, Đường Quế Dương, Xã Cát Quế, Huyện Hoài Đức, Hà Nội','teacher'),(4,'pbkdf2_sha256$1000000$ShwfRtbLgqCmDHPexYaFev$//G82e6pBggX8nFUIQbnbxiYie+CFxdMGNwmYck3VAk=','2025-08-13 14:13:18.782490',0,'TestRegister','','','test@gmail.com',0,1,'2025-08-13 14:13:17.994664','Nguyễn','Kiên',1,'Số 1, Ngõ 85, Đường Quế Dương, Xã Cát Quế, Huyện Hoài Đức, Hà Nội','expert'),(5,'pbkdf2_sha256$1000000$YnB6ERatcE8EH79yvt2ifO$GE7yN8dp+LmlfxKhmj2mpKuxnpVQR/VATMy1KfHrIlM=','2025-08-13 14:33:44.042590',0,'Duongtung1512','','','doduongg2004@gmail.com',0,1,'2025-08-13 14:33:43.249314','Đỗ ','Tùng Dương',21,'Khu Trung Tâm','teacher'),(6,'pbkdf2_sha256$1000000$RVhx9YyPMkEYJbdwvDG8ze$fhywNUB7L/yB3EZacBH1GzMkF9LhE8ZxBY4s4MgSS80=','2025-08-14 01:05:16.369758',0,'NguyenTuKien218','','','nguyentukien@gmail.com',0,1,'2025-08-14 01:05:15.587129','Nguyễn','Kiên',30,'Số 1, Ngõ 85, Đường Quế Dương, Xã Cát Quế, Huyện Hoài Đức, Hà Nội','teacher');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_customuser_id_group_id_3c656da4_uniq` (`customuser_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_customuser_id_62675d7c_fk_auth_user_id` FOREIGN KEY (`customuser_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissio_customuser_id_permission_f01ff6bf_uniq` (`customuser_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_customuser_id_843d9bac_fk_auth_user` FOREIGN KEY (`customuser_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2025-08-12 11:01:48.875961','1','Theo đối tượng',1,'[{\"added\": {}}]',9,1),(2,'2025-08-12 11:02:11.333157','2','Theo lĩnh vực',1,'[{\"added\": {}}]',9,1),(3,'2025-08-12 11:02:23.775611','3','Theo thể loại',1,'[{\"added\": {}}]',9,1),(4,'2025-08-12 11:02:34.115193','4','Theo khu vực',1,'[{\"added\": {}}]',9,1),(5,'2025-08-12 11:02:55.953140','5','Lớp 1',1,'[{\"added\": {}}]',9,1),(6,'2025-08-12 11:03:18.970315','6','Lớp 2',1,'[{\"added\": {}}]',9,1),(7,'2025-08-12 11:03:30.555231','7','Lớp 3',1,'[{\"added\": {}}]',9,1),(8,'2025-08-12 11:03:44.937514','8','Lớp 4',1,'[{\"added\": {}}]',9,1),(9,'2025-08-12 11:04:12.287362','9','Lớp 5',1,'[{\"added\": {}}]',9,1),(10,'2025-08-12 11:04:54.914966','10','Khoa học',1,'[{\"added\": {}}]',9,1),(11,'2025-08-12 11:05:27.935660','11','Toán học',1,'[{\"added\": {}}]',9,1),(12,'2025-08-12 11:05:44.169750','12','Tự nhiên - Xã hội',1,'[{\"added\": {}}]',9,1),(13,'2025-08-12 11:05:58.636195','13','Địa lý - Lịch sử',1,'[{\"added\": {}}]',9,1),(14,'2025-08-12 11:06:18.386734','14','Công nghệ',1,'[{\"added\": {}}]',9,1),(15,'2025-08-12 11:06:38.592323','15','Nghệ thuật',1,'[{\"added\": {}}]',9,1),(16,'2025-08-12 11:07:03.750559','16','Bài giảng',1,'[{\"added\": {}}]',9,1),(17,'2025-08-12 11:07:20.213108','17','Giáo trình',1,'[{\"added\": {}}]',9,1),(18,'2025-08-12 11:07:34.186953','18','Bài tập',1,'[{\"added\": {}}]',9,1),(19,'2025-08-12 11:07:50.564889','19','Bài kiểm tra',1,'[{\"added\": {}}]',9,1),(20,'2025-08-12 11:08:11.102778','20','Thể loại khác',1,'[{\"added\": {}}]',9,1),(21,'2025-08-12 11:08:26.242720','21','Hà Nội',1,'[{\"added\": {}}]',9,1),(22,'2025-08-12 11:08:39.812840','22','Hà Tĩnh',1,'[{\"added\": {}}]',9,1),(23,'2025-08-12 11:08:51.679611','23','Nghệ An',1,'[{\"added\": {}}]',9,1),(24,'2025-08-12 11:09:03.741145','24','Khu vực khác',1,'[{\"added\": {}}]',9,1),(25,'2025-08-12 11:09:27.492764','24','Khu vực khác',2,'[{\"changed\": {\"fields\": [\"Parent\"]}}]',9,1),(26,'2025-08-13 10:34:03.636670','2','kien',3,'',14,1),(27,'2025-08-14 02:32:42.554257','1','CHUYÊN ĐỀ CÁC VÙNG KINH TẾ',3,'',7,1),(28,'2025-08-14 02:51:30.294254','2','Giới thiệu về nền tảng STEMIND',2,'[{\"changed\": {\"fields\": [\"Title\", \"Categories\", \"File description\", \"File thumbnail\"]}}]',7,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(10,'Chatbot','chatmessage'),(11,'Chatbot','chatsession'),(12,'Chatbot','fileattachment'),(4,'contenttypes','contenttype'),(9,'File_sharing_platform','category'),(6,'File_sharing_platform','favorite'),(7,'File_sharing_platform','file'),(8,'File_sharing_platform','fileextension'),(5,'sessions','session'),(18,'Social_Platform','comment'),(14,'Social_Platform','customuser'),(19,'Social_Platform','like'),(13,'Social_Platform','pointsettings'),(17,'Social_Platform','pointtransaction'),(16,'Social_Platform','post'),(15,'Social_Platform','userprofile');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-08-12 10:57:42.591669'),(2,'contenttypes','0002_remove_content_type_name','2025-08-12 10:57:42.806344'),(3,'auth','0001_initial','2025-08-12 10:57:43.412773'),(4,'auth','0002_alter_permission_name_max_length','2025-08-12 10:57:43.544857'),(5,'auth','0003_alter_user_email_max_length','2025-08-12 10:57:43.557092'),(6,'auth','0004_alter_user_username_opts','2025-08-12 10:57:43.569246'),(7,'auth','0005_alter_user_last_login_null','2025-08-12 10:57:43.582234'),(8,'auth','0006_require_contenttypes_0002','2025-08-12 10:57:43.590144'),(9,'auth','0007_alter_validators_add_error_messages','2025-08-12 10:57:43.604778'),(10,'auth','0008_alter_user_username_max_length','2025-08-12 10:57:43.616506'),(11,'auth','0009_alter_user_last_name_max_length','2025-08-12 10:57:43.628341'),(12,'auth','0010_alter_group_name_max_length','2025-08-12 10:57:43.655700'),(13,'auth','0011_update_proxy_permissions','2025-08-12 10:57:43.671962'),(14,'auth','0012_alter_user_first_name_max_length','2025-08-12 10:57:43.683981'),(15,'Social_Platform','0001_initial','2025-08-12 10:57:46.001936'),(16,'Chatbot','0001_initial','2025-08-12 10:57:46.159513'),(17,'Chatbot','0002_initial','2025-08-12 10:57:46.578678'),(18,'File_sharing_platform','0001_initial','2025-08-12 10:57:46.898090'),(19,'File_sharing_platform','0002_initial','2025-08-12 10:57:47.938840'),(20,'admin','0001_initial','2025-08-12 10:57:48.269748'),(21,'admin','0002_logentry_remove_auto_add','2025-08-12 10:57:48.291564'),(22,'admin','0003_logentry_add_action_flag_choices','2025-08-12 10:57:48.314733'),(23,'sessions','0001_initial','2025-08-12 10:57:48.403399');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('jicb7wizdesb7og38bf76dad7xmylakw','.eJxVjDEOAiEQRe9CbQg7gKClvWcgwwzIqoFk2a2Md1eSLbT9773_EgG3tYStpyXMLM5iEoffLSI9Uh2A71hvTVKr6zJHORS50y6vjdPzsrt_BwV7GfURLbnsT5TBawvgNFoPHj0bIs2WOJMCbZwFk6zXJn6hcjwBIGYl3h_fVzeb:1umCY1:rZJ5_6fwlZQEneY_fZMffloPLc6176ryGZCVzu_QsdI','2025-08-27 14:33:49.927096'),('jw0txmkzwj3mhkrmr1un7g3y2sf3evax','.eJxVjDEOAiEQRe9CbQg7gKClvWcgwwzIqoFk2a2Md1eSLbT9773_EgG3tYStpyXMLM5iEoffLSI9Uh2A71hvTVKr6zJHORS50y6vjdPzsrt_BwV7GfURLbnsT5TBawvgNFoPHj0bIs2WOJMCbZwFk6zXJn6hcjwBIGYl3h_fVzeb:1umMQ5:HDKVgUNLTCqheWFtlMNcDgeGgMVQLUMWE6tEEZZ2yb4','2025-08-28 01:06:17.563301'),('u88gd76m6p73arsgok0mj30k8eljms36','.eJxVjDsOwjAQBe_iGllre5cESnrOEK0_iwPIluKkQtwdLKWA9s3Me6mJtzVPW0vLNEd1VqQOv5vn8Eilg3jncqs61LIus9dd0Ttt-lpjel529-8gc8u9_qpGyBLAIAiBbTxhHD2jBWbn0JGPjEbSeAQRQwZpAMuExoKQqPcH7143pw:1umCXw:L8wJX2f6kkF45LPE4kYkyjReEWl5I0Mz5IgAVwY0edE','2025-08-27 14:33:44.055110');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-14 11:58:34
