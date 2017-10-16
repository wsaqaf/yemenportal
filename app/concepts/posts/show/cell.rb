class Posts::Show::Cell < Application::Cell
  private

  def post
    model
  end

  def header_url
    post_header_url(post, protocol: post_header_protocol)
  end

  def post_header_protocol
    ::Rails.application.config_for(:external_site_embedding)["post_header_protocol"]
  end

  delegate :link, to: :post, prefix: true, allow_nil: true
end
