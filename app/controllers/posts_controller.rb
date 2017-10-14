class PostsController < ApplicationController
  def show
    render html: "ada"
  end

  private

  def post
    Post.find(params[:id])
  end
end
