class HomePageController < ApplicationController
  def index
    @posts = Post.paginate(page: params[:page], per_page: 1).order("pub_date DESC")
    render cell: true, model: @posts
  end
end
