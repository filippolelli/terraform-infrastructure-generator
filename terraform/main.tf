# generated file

resource "kubernetes_namespace" "node-backend_namespace" {
  metadata {
    name = "node-backend"
  }
}


resource "kubernetes_deployment" "node-backend_deployment_1702565266987789159" {
    metadata {
        generate_name = "node-backend-deployment-"
        labels = {
            app = "node-backend_1702565266987789159"
        }
        namespace = kubernetes_namespace.node-backend_namespace.metadata.0.name
    }
    spec {
        replicas = 1
        selector {
            match_labels = {
                app = "node-backend_1702565266987789159"
            }
        }
        template {
            metadata {
                generate_name = "node-backend-app-"
                labels = {
                    app = "node-backend_1702565266987789159"
                }
            }
            spec {
                container {
                    image = "filippolelli/node-backend"
                    name  = "node-backend-container"
                }
            }
        }
    }
}


resource "kubernetes_namespace" "mysql_namespace" {
  metadata {
    name = "mysql"
  }
}


resource "kubernetes_pod" "mysql_pod_1702565266987958137" {
  metadata {
    name = "mysql-pod-1702565266987958137"
    labels = {
      app = "mysql_1702565266987958137"
    }
    namespace = kubernetes_namespace.mysql_namespace.metadata.0.name
  }
  spec {
    container {
      image = "mysql"
      name  = "mysql-container"

      env {
        name  = "MYSQL_ROOT_PASSWORD"
        value = "password"
      }
    }
    

    
  }
}


resource "kubernetes_namespace" "react-frontend_namespace" {
  metadata {
    name = "react-frontend"
  }
}


resource "kubernetes_deployment" "react-frontend_deployment_1702565266988105000" {
    metadata {
        generate_name = "react-frontend-deployment-"
        labels = {
            app = "react-frontend_1702565266988105000"
        }
        namespace = kubernetes_namespace.react-frontend_namespace.metadata.0.name
    }
    spec {
        replicas = 1
        selector {
            match_labels = {
                app = "react-frontend_1702565266988105000"
            }
        }
        template {
            metadata {
                generate_name = "react-frontend-app-"
                labels = {
                    app = "react-frontend_1702565266988105000"
                }
            }
            spec {
                container {
                    image = "filippolelli/react-frontend"
                    name  = "react-frontend-container"
                }
            }
        }
    }
}

resource "kubernetes_service" "mysql_service_1702565266988237070" {
  metadata {
    name = "mysql-service"
    namespace = kubernetes_namespace.mysql_namespace.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_pod.mysql_pod_1702565266987958137.metadata.0.labels.app
    }
    port {
      port        = 8080
      target_port = 3306
       
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_service" "react-frontend_service_1702565266988293223" {
  metadata {
    name = "react-frontend-service"
    namespace = kubernetes_namespace.react-frontend_namespace.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.react-frontend_deployment_1702565266988105000.metadata.0.labels.app
    }
    port {
      port        = 8080
      target_port = 3000
      node_port = 31225 
    }

    type = "NodePort"
  }
}

resource "kubernetes_service" "node-backend_service_1702565266988325054" {
  metadata {
    name = "node-backend-service"
    namespace = kubernetes_namespace.node-backend_namespace.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.node-backend_deployment_1702565266987789159.metadata.0.labels.app
    }
    port {
      port        = 8080
      target_port = 3000
      node_port = 30971 
    }

    type = "NodePort"
  }
}
