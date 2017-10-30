class Posts::Index::Cell < Application::Cell
  CLUSTER_MODE_RELATED_POSTS_COUNT = 3
  DEFAULT_RELATED_POSTS_COUNT = 0

  private

  def posts
    model
  end

  def related_posts_count
    if cluster_mode?
      CLUSTER_MODE_RELATED_POSTS_COUNT
    else
      DEFAULT_RELATED_POSTS_COUNT
    end
  end

  def cluster_mode?
    post_filter_params.set == :most_covered
  end

  def post_filter_params
    @_post_filter_params ||= Posts::Filter::Params.new(params)
  end
end
