class Posts::Show::Cell < Application::Cell
  private

  def post
    model
  end

  delegate :link, to: :post, prefix: true, allow_nil: true
end
