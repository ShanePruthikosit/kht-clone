<?php
//index.php
// NB: This file is obsolete. We use index.html instead


$error = '';
$village_name = '';
$article_url = '';
$article_name = '';
$article_date = '';

function clean_text($string)
{
    $string = trim($string);
    $string = stripslashes($string);
    $string = htmlspecialchars($string);
    return $string;
}

session_start();

if(isset($_POST["submit"]))
{
    if(empty($_POST["village_name"]))
    {
        $error .= '<p><label class="text-danger">Please Enter the village name</label></p>';
    }
    else
    {
        $village_name = clean_text($_POST["village_name"]);
        if(!preg_match("/^[a-zA-Z0-9 ]*$/",$village_name))
        {
            $error .= '<p><label class="text-danger">Only letters, numbers and white space allowed</label></p>';
        }
    }
    if(empty($_POST["article_url"]))
    {
        $error .= '<p><label class="text-danger">Please Enter article URLs</label></p>';
    }
    else
    {
        $article_url = clean_text($_POST["article_url"]);
    }
    if(!empty($_POST["article_name"]))
    {
        $article_name = clean_text($_POST["article_name"]);
    }
    if(!empty($_POST["article_date"]))
    {
        $article_date = clean_text($_POST["article_date"]);
        $d = DateTime::createFromFormat('d/m/Y', $article_date);
        if($d && $d->format('d/m/Y') === $article_date)
        {
            // $article_date is valid
        } 
        else 
        {
            $error .= '<p><label class="text-danger">Invalid date format. Use DD/MM/YYYY.</label></p>';
        }
    }
    if($error == '')
    {
        $file_open = fopen("post_data.csv", "a");
        $no_rows = count(file("post_data.csv"));
        if($no_rows > 1)
        {
            $no_rows = ($no_rows - 1) + 1;
        }
        $form_data = array(
            'sr_no'  => $no_rows,
            'village_name'  => $village_name,
            'article_url'  => $article_url,
            'article_name' => $article_name,
            'article_date' => $article_date
        );
        fputcsv($file_open, $form_data);

        $url = "https://kht-map.org:2546/api/post/village_url";

        $options = array(
        'http' => array(
            'header'  => "Content-type: application/x-www-form-urlencoded",
            'method'  => 'POST',
            'content' => http_build_query($form_data)
        )
        );
        $context  = stream_context_create($options);
        $resp = file_get_contents($url, false, $context);
        echo $resp;

        $village_name = '';
        $article_url = '';
        $article_name = '';
        $article_date = '';

        // Store the success message in the session
        $_SESSION['message'] = 'Thank you for creating new post';

        // Redirect to the same page
        header("Location: index.php", true, 303);
        exit;
    }
}

?>
<!DOCTYPE html>
<html>
 <head>
  <title>Add new post</title>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" />
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
 <link rel="stylesheet" type="text/css" href="stylesheet.css">
 </head>
 <body>
  <br />
  <div class="container">
   <h2 align="center">Add new post</h2>
   <br />
   <div class="col-md-6" style="margin:0 auto; float:none;">
    <form method="post">
     <br />
     <?php if(isset($_SESSION['message'])): ?>
        <p class="text-success"><?php echo $_SESSION['message']; ?></p>
        <?php unset($_SESSION['message']); ?>
     <?php endif; ?>
     <?php echo $error; ?>
     <div class="form-group">
      <label>Village Name</label>
      <input type="text" name="village_name" placeholder="Enter Village Name" class="form-control" value="<?php echo $name; ?>" />
     </div>
     <div class="form-group">
      <label>Article URL</label>
      <input type="text" name="article_url" class="form-control" placeholder="Enter Article URL" value="<?php echo $email; ?>" />
     </div>
     <div class="form-group">
      <label>Article Name</label>
      <input type="text" name="article_name" class="form-control" placeholder="Enter Article Name" value="<?php echo $subject; ?>" />
     </div>
     <div class="form-group">
      <label>Article Date</label>
      <input type="text" name="article_date" class="form-control" placeholder="Enter Article Date (ex. dd/mm/yyyy)" value="<?php echo $subject; ?>" />
     </div>
     <div class="form-group" align="center">
      <input type="submit" name="submit" class="btn btn-info" value="Submit" />
     </div>
    </form>
   </div>
  </div>
 </body>
</html>
