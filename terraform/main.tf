provider "aws" {
  region = "${var.region}"
}

resource "aws_dynamodb_table" "signal-hotel" {
  name           = "Rooms"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "roomName"

  attribute = [{
    name = "roomName"
    type = "S"
  }
  ]
}
