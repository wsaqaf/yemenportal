class Posts::Show::Cell < Application::Cell
  private

  def post
    model
  end

  def header_url
    posts_header_url(post)
  end

  delegate :link, to: :post, prefix: true, allow_nil: true
end
