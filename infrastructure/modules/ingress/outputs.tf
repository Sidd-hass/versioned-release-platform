output "alb_controller_policy_arn" {
  description = "ARN of the IAM policy for AWS Load Balancer Controller"
  value       = aws_iam_policy.alb_controller.arn
}

output "alb_controller_role_arn" {
  description = "ARN of the IRSA role for AWS Load Balancer Controller"
  value       = aws_iam_role.alb_controller_irsa.arn
}

output "helm_set_command" {
  description = "Helm set argument snippet for serviceAccount.annotations"
  value       = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn=${aws_iam_role.alb_controller_irsa.arn}"
}
