class Posts::Show::Cell < Application::Cell
  private

  def post
    model
  end

  def header_url
    post_header_url(post, protocol: protocol)
  end

  def protocol
    ::Rails.env.production? ? "https" : "http"
  end

  delegate :link, to: :post, prefix: true, allow_nil: true
end
