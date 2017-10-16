class Posts::Headers::Show::Cell < Application::Cell
  private

  def post
    model
  end

  delegate :topic, :link, to: :post, prefix: true, allow_nil: true
end
