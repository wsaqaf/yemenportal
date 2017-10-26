class Posts::CategoriesUpdater
  def initialize(params)
    @params = params
  end

  def updated_category_names
    update_post_with_categories
    post_category_names
  end

  private

  attr_reader :params

  def update_post_with_categories
    post.update(categories: categories)
  end

  def post_category_names
    post.category_names.join(", ")
  end

  def post
    @_post ||= ::Post.find(params[:post_id])
  end

  def categories
    @_categories ||= ::Category.where(id: params[:category_ids])
  end
end
