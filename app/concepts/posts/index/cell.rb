class Posts::Index::Cell < Application::Cell
  RELATED_POSTS_COUNT = 3

  private

  def posts
    model
  end

  def post_filter_params
    Posts::Filter::Params.new(params)
  end
end
