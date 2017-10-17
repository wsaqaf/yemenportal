class Posts::Index::Cell < Application::Cell
  private

  def posts
    model
  end

  def post_filter_params
    Posts::Filter::Params.new(params)
  end
end
