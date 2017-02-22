class HomePageController < ApplicationController
  def index
    category = Category.find_by(name: params[:category])
    if category
      posts = category.posts.paginate(page: params[:page], per_page: 20).ordered_by_publication_date
    else
      posts = Post.paginate(page: params[:page], per_page: 20).ordered_by_publication_date
    end
    render cell: true, model: posts, options: { categories: Category.all }
  end
end
