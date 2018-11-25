provider "aws" {
  region = "us-east-2"
}

resource "aws_dynamodb_table" "signal-hotel" {
  name           = "Rooms"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "RoomName"

  attribute = [{
    name = "RoomName"
    type = "S"
  }
  ]
}
