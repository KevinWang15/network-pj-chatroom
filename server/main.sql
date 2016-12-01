/*
Navicat SQLite Data Transfer

Source Server         : chatroom
Source Server Version : 20817
Source Host           : :0

Target Server Type    : SQLite
Target Server Version : 20817
File Encoding         : 65001

Date: 2016-11-30 14:53:47
*/

PRAGMA foreign_keys = OFF;

-- ----------------------------
-- Table structure for friends
-- ----------------------------
CREATE TABLE "friends" (
"from_user_id"  INTEGER NOT NULL,
"to_user_id"  INTEGER NOT NULL,
"accepted"  TEXT,
PRIMARY KEY ("from_user_id" ASC, "to_user_id")
);

-- ----------------------------
-- Table structure for rooms
-- ----------------------------
CREATE TABLE "rooms" (
"id"  INTEGER NOT NULL,
"room_name"  TEXT,
PRIMARY KEY ("id")
);

-- ----------------------------
-- Table structure for room_user
-- ----------------------------
CREATE TABLE "room_user" (
"id"  INTEGER NOT NULL,
"room_id"  INTEGER,
"user_id"  INTEGER,
PRIMARY KEY ("id")
);

-- ----------------------------
-- Table structure for users
-- ----------------------------
CREATE TABLE "users" (
"id"  INTEGER NOT NULL,
"username"  TEXT,
"password"  TEXT,
"nickname"  TEXT,
PRIMARY KEY ("id" ASC)
);
