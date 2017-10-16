module LayoutHelper
  def post_header_base_link
    root_url(protocol: post_header_protocol)
  end

  private

  def post_header_protocol
    Rails.application.config_for(:external_site_embedding)["post_header_protocol"]
  end
end
