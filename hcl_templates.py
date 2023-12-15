pod_definition_template='''
resource "kubernetes_pod" "{stringable_name}_pod_{random_feed}" {{
  metadata {{
    name = "{stringable_name}-pod-{random_feed}"
    labels = {{
      app = "{stringable_name}_{random_feed}"
    }}
    namespace = {namespace_name}
  }}
  spec {{
    container {{
      image = "{image}"
      name  = "{stringable_name}-container"
    }}

    
  }}
}}
'''

deployment_definition_template='''
resource "kubernetes_deployment" "{stringable_name}_deployment_{random_feed}" {{
    metadata {{
        generate_name = "{stringable_name}-deployment-"
        labels = {{
            app = "{stringable_name}_{random_feed}"
        }}
        namespace = {namespace_name}
    }}
    spec {{
        replicas = {replicas}
        selector {{
            match_labels = {{
                app = "{stringable_name}_{random_feed}"
            }}
        }}
        template {{
            metadata {{
                generate_name = "{stringable_name}-app-"
                labels = {{
                    app = "{stringable_name}_{random_feed}"
                }}
            }}
            spec {{
                container {{
                    image = "{image}"
                    name  = "{stringable_name}-container"
                }}
            }}
        }}
    }}
}}
'''


service_definition_template = '''
resource "kubernetes_service" "{stringable_name}_service_{random_feed}" {{
  metadata {{
    name = "{stringable_name}-service"
    namespace = {namespace_name}
  }}
  spec {{
    selector = {{
      app = {deployment_app_label}
    }}
    port {{
      port        = 8080
      target_port = {target_port}
      {node_port} 
    }}

    type = "{service_type}"
  }}
}}
'''

namespace_definition_template ='''

resource "kubernetes_namespace" "{stringable_name}_namespace" {{
  metadata {{
    name = "{stringable_name}"
  }}
}}

'''