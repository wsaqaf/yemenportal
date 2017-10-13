class Proxy::PostsController < ApplicationController
  def show
    if post.link.start_with?("https")
      redirect_to post.link
    else
      render html: post.page_content
    end
  end

  private

  def post
    Post.find(params[:id])
  end
end
