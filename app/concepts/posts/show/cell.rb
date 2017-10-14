class Posts::Show::Cell < Application::Cell
  private

  def post
    model
  end

  def header_url
    URI.join(@options[:host], posts_header_path(post))
  end

  delegate :link, to: :post, prefix: true, allow_nil: true
end
