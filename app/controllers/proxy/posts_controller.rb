class Proxy::PostsController < ApplicationController
  def show
    render html: post.page_content
  end

  private

  def post
    Post.find(params[:id])
  end
end
