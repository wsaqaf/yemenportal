class HomePageController < ApplicationController
  def index
    @posts = Post.paginate(page: params[:page], per_page: 20).order('pub_date DESC')
  end
end
