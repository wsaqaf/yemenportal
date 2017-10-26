class Posts::Reviews::Categories::Cell < Application::Cell
  private

  property :category_ids

  def post
    model
  end

  def all_categories
    Category.all
  end
end
