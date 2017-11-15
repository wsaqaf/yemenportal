class Posts::Index::Spotlight::Cell < Application::Cell
  private

  def post_filter_params
    model
  end

  def set_options
    Posts::Filter::Params.set.options
  end

  def time_options
    Posts::Filter::Params.time.options
  end

  def source_options
    Source.not_deleted
  end

  def categories_options
    Category.all
  end
end
