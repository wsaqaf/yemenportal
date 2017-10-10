module SocialsHelper
  def facebook_link
    social_links.fetch("facebook")
  end

  def twitter_link
    social_links.fetch("twitter")
  end

  private

  def social_links
    Rails.application.secrets.socials
  end
end
