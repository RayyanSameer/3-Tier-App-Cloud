resource "aws_ecr_repository" "todo-frontend-repo" {
  name                 = "todo-frontend-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "todo-backend-repo" {
  name                 = "todo-backend-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}